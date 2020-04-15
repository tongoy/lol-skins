# -*- coding: utf-8 -*-

"""
This script aims to download LOL hero skins from https://lol.qq.com/data/info-heros.shtml.
"""


import re
import os
import json
import requests


class SkinParser(object):
    def __init__(self, dirs):
        self.num_heroes = 0
        self.num_skins = 0
        self.num_notfound = 0
        self.notfound_urls = []
        self.dirs = dirs

        # javascript url
        self.heroes_url = r'https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js'
        self.hero_url = r'http://game.gtimg.cn/images/lol/act/img/js/hero/{:s}.js'

        # hero images
        self.avatar_url = r'https://game.gtimg.cn/images/lol/act/img/champion/{:s}.png'
        self.skin_url = r'https://game.gtimg.cn/images/lol/act/img/skin/{:s}{:s}.jpg'
        self.loading_url = r'https://game.gtimg.cn/images/lol/act/img/skinloading/{:s}.jpg'
        self.source_url = r'https://game.gtimg.cn//images/lol/act/img/guidetop/guide{:s}.jpg'

        # hero audio
        self.audio_url = r'https://game.gtimg.cn/images/lol/act/img/vo/{:s}/{:s}.ogg'


        if not os.path.isdir(dirs['js']):
            os.makedirs(dirs['js'])


    def download(self, url, filename=''):
        if filename == '':
            filename = url.split('/')[-1]

        r = requests.get(url=url)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
        elif r.status_code == 404:
            self.num_notfound += 1
            self.notfound_urls.append(url)
        else:
            r.raise_for_status()


    def parse_heroid(self):
        js_filename = os.path.join(self.dirs['js'], self.heroes_url.split('/')[-1])
        self.download(self.heroes_url, js_filename)

        with open(js_filename, 'r') as f:
            hero_data = json.load(f)
            version = hero_data['version']
            filetime = hero_data['fileTime']
            hero_list = hero_data['hero']

            print("update {:s}".format(filetime))
            print("{:d} heroes detected, ver {:s}".format(len(hero_list), version))

            for i, h in enumerate(hero_list):
                self.num_heroes += 1
                self.download_heroskin(i, h)

        print("\n{:d} heroes, {:d} skins downloaded :)".format(self.num_heroes, self.num_skins))

        if self.num_notfound:
            print("{:d} files not found".format(self.num_notfound))
            print(self.notfound_urls)


    def download_heroskin(self, i, hero):
        js_filename = os.path.join(self.dirs['js'], '{:s}-{:s}.js'.format(hero['heroId'], hero['alias']))
        self.download(self.hero_url.format(hero['heroId']), js_filename)

        with open(js_filename, 'r') as f:
            hero_data = json.load(f)
            version = hero_data['version']
            filetime = hero_data['fileTime']
            info = hero_data['hero']
            skins = hero_data['skins']

            heroid = info['heroId']
            name = info['name']
            alias = info['alias']
            title = info['title']

            print("[{:d}] heroid: {:s}, name: {:s}, title: {:s}, alias: {:s}".format(i+1, heroid, name, title, alias))

            # make dirs
            dirs = {}
            for d in self.dirs['hero']:
                dirs[d] = self.dirs['hero'][d].format(name+' '+title)
                if not os.path.isdir(dirs[d]):
                    os.makedirs(dirs[d])

            num_skins = 0
            for j in range(len(skins)):
                if skins[j]['chromas'] == '1':
                    continue
                num_skins += 1
                skinid = skins[j]['skinId']
                skinname = skins[j]['name']
                print("    skinid: {:s}, name: {:s}".format(skinid, skinname))

                skinname = re.sub(r'[\\/:*?"<>|]+', '', skinname)

                self.download(
                    self.skin_url.format('big', skinid),
                    os.path.join(dirs['skin_big'], skinname+'.'+self.skin_url.split('.')[-1])
                )

                # self.download(
                #     self.skin_url.format('small', skinid),
                #     os.path.join(dirs['skin_small'], skinname+'.'+self.skin_url.split('.')[-1])
                # )

                self.download(
                    self.loading_url.format(skinid),
                    os.path.join(dirs['loading'], skinname+'.'+self.loading_url.split('.')[-1])
                )

                # self.download(
                #     self.source_url.format(skinid),
                #     os.path.join(dirs['source'], skinname+'.'+self.source_url.split('.')[-1])
                # )

            self.num_skins += num_skins

            # self.download(
            #     self.avatar_url.format(alias),
            #     os.path.join(dirs['avatar'], alias + '.' + self.avatar_url.split('.')[-1])
            # )

            # for v in ['choose', 'ban']:
            #     self.download(
            #         self.audio_url.format(v, heroid),
            #         os.path.join(dirs['audio'], v + heroid + '.' + self.audio_url.split('.')[-1])
            #     )

            print("    ===> {:d} skins downloaded".format(num_skins))



if __name__ == '__main__':

    dirs = {
        'js': 'lolhero/js',
        'hero': {
            # 'avatar': 'lolhero/hero/{:s}/avatar',
            # 'audio': 'lolhero/hero/{:s}/audio',
            #'skin_small': 'lolhero/hero/{:s}/skin_small',
            'skin_big': 'lolhero/hero/{:s}/skin_big',
            'loading': 'lolhero/hero/{:s}/loading',
            #'source': 'lolhero/hero/{:s}/source'
        }
    }


    parser = SkinParser(dirs)
    parser.parse_heroid()

























































