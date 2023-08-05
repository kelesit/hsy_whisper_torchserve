# hsy_whisper_torchserve

serve on Mac locally
## environment
pip install torchserve torch-model-archiver torch-workflow-archiver

### Model archive
torch-model -archiver --model-name whisper_test --model-file ./whisper/model.py --serialized-file base.en.pt --extra-file whisper,hsyhandler.py --export-path model_store --handler ./hsyhandler.py --version 1.0

[details](https://pytorch.org/serve/getting_started.html#store-a-model)

### Start TorchServe to serve the model
torchserve --start --ncs --model-store model_store --models whipser_test.mar

### test
python send_request.py
