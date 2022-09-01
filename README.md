# Streamlit with Snowflake
Base on this event: https://www.linkedin.com/events/snowflake-streamlit6969003201526128640/comments/  

Example application demonstrating some features of [streamlit](https://streamlit.io/).

## Usage
>**Note:** This example uses conda to manage the environment, but pyenv or other env managers can be used if preferred. [Installing conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)

```bash
conda create -n sl_demo python=3.8  
conda activate sl_demo  
pip3 install -r requirements.txt  
streamlit run app.py  
```

## Containerize app
Build image:  
```docker build -t streamlit .```

Run image locally:  
```docker run -p 8501:8501 streamlit```

> TODO: Send to ECS
  
