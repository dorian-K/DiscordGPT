# DiscordGPT

## Getting started

Running via Docker is recommended. First build the image:

`sudo docker build -t discordgpt .`

Then run the container:

`sudo docker run -it -e OPENAI_API_KEY='your key goes here' -e DISCORD_TOKEN='your token here' discordgpt`

Remember to fill in your OpenAI and discord api tokens.

## Showcase

![Simple Multi-Message conversation](asset/simple_multi_message.webm)

![Complex Multi-Message conversation](asset/complex_multi_message.webm)