#!/bin/bash

cd Iman-j
uv sync
uv add parsivar


sudo cp bot.service /etc/systemd/system/
sudo cp fastapi.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl enable bot
