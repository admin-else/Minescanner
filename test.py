import requests
from bs4 import BeautifulSoup
import socket
import os
import subprocess
import multiprocessing
import pinger
import Scraper
import concurrent.futures

Scraper.try2ping('mc.hypixel.net')