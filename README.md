# DiscordGPT

## How it works
DiscordGPT is a Discord bot that connects to the OpenAI ChatGPT API. The bot is triggered when a message containing a question mark or an @ mention is sent.

Upon activation, the bot collects up to five previous messages from the chat history and sends them to the ChatGPT API to generate a response.

To ensure the conversation stays respectful, the bot monitors both the input and output to the ChatGPT API for any inappropriate language.

## Getting started

Running via Docker is recommended. First build the image:

`sudo docker build -t discordgpt .`

Then run the container:

`sudo docker run -it -e OPENAI_API_KEY='your key goes here' -e DISCORD_TOKEN='your token here' discordgpt`

Remember to fill in your OpenAI and discord API keys.

## Showcase

https://user-images.githubusercontent.com/62394594/223112050-0dca2692-44cf-4d53-a93a-48460c762f64.mp4



https://user-images.githubusercontent.com/62394594/223112313-c2c3ed7c-102b-4a37-a80a-91dac2f5cb1b.mp4

