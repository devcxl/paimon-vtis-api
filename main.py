
import soundfile as sf
import torch
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import FileResponse,StreamingResponse
import hashlib
import torch
from storage import Model, SQLiteDB, VitsHistory, User
import utils
import commons
from models import SynthesizerTrn
from text.symbols import symbols
from text import text_to_sequence
import time
from typing import Annotated
import uuid

def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm).cpu()
    return text_norm


def calculate_md5(text):
    md5_hash = hashlib.md5(text.encode())
    return md5_hash.hexdigest()


hps = utils.get_hparams_from_file("config/biaobei_base.json")

net_g = SynthesizerTrn(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    **hps.model).cpu()
_ = net_g.eval()

_ = utils.load_checkpoint('/save/vits/models/G_1434000.pth', net_g, None)


db = SQLiteDB('new.sqlite')
Model.initialize(db)
try:
    VitsHistory.create_table()
    User.create_table()
    user_total = User.total()
    print(user_total)
    if user_total == 0:
        set_token = uuid.uuid4().hex
        insert=User()
        insert.access_token = set_token
        insert.save()
        print(set_token)
except Exception as e:
    pass

app = FastAPI()
audio_path ='paimon.wav'

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/api/paimon")
async def paimon(content: str = '你好，我是派蒙。', speed: float = 1.0, access_token: Annotated[str | None, Header()] = None):
    if len(content) > 300:
        raise HTTPException(status_code=401, detail="Content too long")
    user = User.fetch_one('access_token=?', (access_token,))
    if user is not None:
        history = VitsHistory()
        history.user_id = user.id
        history.content = content
        history.save()
        
        stn_tst = get_text(content, hps)
        with torch.no_grad():
            x_tst = stn_tst.cpu().unsqueeze(0)
            x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cpu()
            audio = net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.8,
                                length_scale=speed)[0][0, 0].data.cpu().float().numpy()
        del stn_tst, x_tst, x_tst_lengths,history,user
        sf.write(audio_path, audio, samplerate=hps.data.sampling_rate)
        return FileResponse(audio_path)
    else:
        raise HTTPException(status_code=401, detail="access_token error")

@app.get("/api/paimon/total")
async def paimon(access_token: Annotated[str | None, Header()] = None):
    user = User.fetch_one('access_token=?', (access_token,))
    history_total = VitsHistory.total('user_id=?', (int(user.id),))
    print(history_total)
    return {'count':history_total}