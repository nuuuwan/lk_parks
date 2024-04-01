'''
python workflows/pipeline_tweet.py --TWTR_BEARER_TOKEN=$env:TWTR_BEARER_TOKEN --TWTR_API_KEY=$env:TWTR_API_KEY --TWTR_API_KEY_SECRET=$env:TWTR_API_KEY_SECRET --TWTR_ACCESS_TOKEN=$env:TWTR_ACCESS_TOKEN --TWTR_ACCESS_TOKEN_SECRET=$env:TWTR_ACCESS_TOKEN_SECRET
'''

from lk_plants import Twtr


def main():
    twtr = Twtr.random()
    twtr.tweet()


if __name__ == "__main__":
    main()
