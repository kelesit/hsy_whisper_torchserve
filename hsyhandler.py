from typing import Dict, List
import os

import torch
from ts.torch_handler.base_handler import BaseHandler
import whisper
import uuid
from pathlib import Path
import logging

from whisper.decoding import DecodingOptions, DecodingResult
from torch.profiler import ProfilerActivity

class WhisperHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.initialized = False

    def initialize(self, ctx):

        properties = ctx.system_properties
        self.manifest = ctx.manifest
        # torch.set_num_threads(4)

        self.map_location = "cpu"
        self.device = torch.device(self.map_location)

        model_dir = properties.get("model_dir")

        self.model = whisper.load_model(
            "base.en",
            download_root=model_dir
        )
        self.model.eval()



        self.option = DecodingOptions(
            task="transcribe",
            language="en",
            temperature=0.0,
            prompt=[],
            without_timestamps=False,
            fp16=False,
        )

        self.initialized = True

    def preprocess(
            self, batch_audio: List[Dict[str, bytes]]
    ) -> List[torch.FloatTensor]:
        batch_mel_spec = []
        for audio_byte in batch_audio:
            tmp_file_path = Path(f"/tmp/{uuid.uuid4()}")
            with open(tmp_file_path, "wb") as f:
                f.write(audio_byte["data"])
            audio = whisper.load_audio(str(tmp_file_path))
            padded_audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(padded_audio).to(self.device)
            batch_mel_spec.append(mel)
            tmp_file_path.unlink()
        return batch_mel_spec

    def inference(self, batch_mel_spec: List[torch.FloatTensor]) -> List[torch.Tensor]:
        list_pred = []
        for tensor in batch_mel_spec:
            result = whisper.decode(self.model, tensor, self.option)
            list_pred.append(result)
        return list_pred

    def postprocess(self, list_infer_pred: List[DecodingResult]) -> List[str]:
        list_result = []
        for infer_pred in list_infer_pred:
            list_result.append(infer_pred.text)
        return list_result
