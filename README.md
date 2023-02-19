# Hackafor API

Installation guide


## Install environment
### Miniconda (recommended)
#### Linux /  Mac / Windows
1. install miniconda from [miniconda site](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
2. run `conda env create -f environment.yml`
3. activate env `conda activate hackafor-api-py310`


### Virtualenv
#### Linux /  Mac
1. Install python 3.10 from [python site](https://www.python.org/)
2. Install virtualenv library `python3 -m pip install virtualenv `
3. Create environment `python3 -m virtualenv venv`
4. activate env `source venv/bin/activate`
4. Install dependencies `pip install -r requirements.txt`

#### Windows
1. Install python 3.10 from [python site](https://www.python.org/)
2. Install virtualenv library `python -m pip install virtualenv`
3. Create environment `python -m virtualenv venv`
4. activate env `venv\Scripts\activate`
4. Install dependencies `pip install -r requirements.txt `


## Add environment variables

This API uses supabase to connect, add `SUPABASE_URL` and `SUPABASE_KEY` to environment variables or `.env` file.

Railway:
* Add environment variable to railway `NIXPACKS_PYTHON_VERSION=3.10` to use python 3.10.

## run server

For development:
* `uvicorn app:app --reload`

Railway:
* it is already configured on the Procfile with `web: uvicorn app:app --host 0.0.0.0 --port $PORT`.