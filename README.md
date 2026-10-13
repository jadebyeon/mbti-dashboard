# MBTI in Writing

An interactive dashboard that shows how much MBTI type shows up in forum writing. Pick a type, then compare it with everyone else.

## Files
- `mbti_app.py` is the dashboard (Streamlit)
- `mbti_dashboard.csv` is the data the dashboard uses
- `avatars/` has one avatar image for each of the 16 types, named like `ENFP.svg`
- `requirements.txt` lists the packages

## Run it
1. Open a terminal in this folder.
2. Install the packages. (python3 -m pip install -r requirements.txt)
3. Start the dashboard. (python3 -m streamlit run mbti_app.py)
4. Open http://localhost:8501 if the browser does not open by itself.

To stop it, press Control + C in the terminal.

## Data
Posts come from the Kaggle MBTI dataset by Mitchell J (https://www.kaggle.com/datasets/datasnaek/mbti-type), collected from the PersonalityCafe forum. After cleaning, 8,600 users remain. Types are self-reported. The measures are keyword counts, so they are rough.

## Credits
Type names, taglines and avatars are from 16Personalities (https://www.16personalities.com/personality-types).