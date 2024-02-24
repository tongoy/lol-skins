# -*- coding: utf-8 -*-
# BY: TONG

"""
The script is used to download lol skins from
https://lol.qq.com/data/info-heros.shtml,
https://101.qq.com/#/hero.
"""

import re
import os
import json
import requests


class Logger(object):
    def __init__(self, log_file):
        if os.path.isfile(log_file):
            os.remove(log_file)
        
        self.log_f = open(log_file, 'a', encoding='utf-8')
    
    def log(self, msg):
        print(msg)
        self.log_f.write(str(msg)+"\n")
        self.log_f.flush()
    
    def close(self):
        self.log_f.close()


class LoLSkins(object):
    def __init__(self, ROOT_DIR='lolhero'):
        self.n_heroes = 0
        self.n_skins = 0
        self.n_notfound = 0
        self.notfound_urls = []
        self.dirs = {
            'js': os.path.join(ROOT_DIR, 'js'),
            'hero': {
                'audio': os.path.join(ROOT_DIR, 'hero'),
                'main': os.path.join(ROOT_DIR, 'hero'),
                'loading': os.path.join(ROOT_DIR, 'hero'),
                # 'icon': os.path.join(ROOT_DIR, 'hero'),
                # 'video': os.path.join(ROOT_DIR, 'hero'),
                # 'source': os.path.join(ROOT_DIR, 'hero')
            }
        }

        # javascript url
        self.heroes_url = r'https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js'
        self.hero_url = r'https://game.gtimg.cn/images/lol/act/img/js/hero/{:s}.js'

        # resources
        self.audio_url = r'https://game.gtimg.cn/images/lol/act/img/vo/{:s}/{:s}.ogg'
        self.main_url = r'https://game.gtimg.cn/images/lol/act/img/skin/big_{:s}.jpg'
        self.loading_url = r'https://game.gtimg.cn/images/lol/act/img/skinloading/{:s}.jpg'
        
        self.icon_url = r'https://game.gtimg.cn/images/lol/act/img/skin/small_{:s}.jpg'
        self.video_url = r'https://game.gtimg.cn/images/lol/act/img/skinvideo/sp_{:s}.jpg'
        self.source_url = r'https://game.gtimg.cn/images/lol/act/img/guidetop/guide_{:s}.jpg'


        if not os.path.isdir(self.dirs['js']):
            os.makedirs(self.dirs['js'])

        self.log_file = os.path.join(ROOT_DIR, 'log.txt')
        self.logger = Logger(self.log_file)


    def _download(self, url, filename=''):
        if filename == '':
            filename = url.split('/')[-1]
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return 1
        elif r.status_code == 404:
            self.n_notfound += 1
            self.notfound_urls.append({os.path.basename(filename):url})
        else:
            r.raise_for_status()
        
        return 0


    def parse_heroes(self):
        js_filename = os.path.join(self.dirs['js'], self.heroes_url.split('/')[-1])
        self._download(self.heroes_url, js_filename)

        with open(js_filename, 'r') as f:
            heroes_data = json.load(f)
            version = heroes_data['version']
            filetime = heroes_data['fileTime']
            heroes_list = heroes_data['hero']
        

        self.logger.log("Version {:s}".format(version))
        self.logger.log("{:d} heroes detected".format(len(heroes_list)))
        self.logger.log("Filetime {:s}".format(filetime))

        for i, h in enumerate(heroes_list):
            self.n_heroes += 1
            self.download_hero(i, h)

        self.logger.log("\n{:d} skins for {:d} heroes downloaded.".format(self.n_skins, self.n_heroes))

        if self.n_notfound:
            self.logger.log("{:d} files not found.".format(self.n_notfound))
            self.logger.log(self.notfound_urls)
        
        self.logger.close()


    def download_hero(self, i, hero):
        js_filename = os.path.join(self.dirs['js'], '{:s}_{:s}.js'.format(hero['heroId'], hero['alias']))
        self._download(self.hero_url.format(hero['heroId']), js_filename)

        with open(js_filename, 'r') as f:
            hero_data = json.load(f)
            version = hero_data['version']
            filetime = hero_data['fileTime']
            info = hero_data['hero']
            skins = hero_data['skins']

            hero_id = info['heroId']
            name = info['name']
            alias = info['alias']
            title = info['title']

        self.logger.log("[{:d}] hero_id: {:s}, name: {:s}, title: {:s}, alias: {:s}".format(i+1, hero_id, name, title, alias))

        # make dirs
        dirs = {}
        for d in self.dirs['hero']:
            dirs[d] = os.path.join(self.dirs['hero'][d], name+' '+title, d)
            if not os.path.isdir(dirs[d]):
                os.makedirs(dirs[d])

        n_skins = 0
        for j in range(len(skins)):
            if skins[j]['chromas'] == '1':
                continue
            
            skin_id = skins[j]['skinId']
            skin_name = skins[j]['name']
            self.logger.log("    skin_id: {:s}, skin_name: {:s}".format(skin_id, skin_name))

            # for filename rules on e.g., Windows
            skin_name = re.sub(r'[\\/:*?"<>|]+', '', skin_name)

            status_code = self._download(skins[j]['mainImg'], os.path.join(dirs['main'], skin_name+'.'+skins[j]['mainImg'].split('.')[-1]))
            if status_code:
                n_skins += 1
            self._download(skins[j]['loadingImg'], os.path.join(dirs['loading'], skin_name+'.'+skins[j]['loadingImg'].split('.')[-1]))
            # self._download(skins[j]['sourceImg'], os.path.join(dirs['source'], skin_name+'.'+skins[j]['sourceImg'].split('.')[-1]))
        
        self.n_skins += n_skins
        self.logger.log("    {:d} skins downloaded".format(n_skins))

        self._download(info['selectAudio'], os.path.join(dirs['audio'], 'pick_'+info['selectAudio'].split('/')[-1]))
        self._download(info['banAudio'], os.path.join(dirs['audio'], 'ban_'+info['selectAudio'].split('/')[-1]))
        self.logger.log("    pick/ban audio downloaded")



if __name__ == '__main__':

    ROOT_DIR = 'lolhero'

    parser = LoLSkins(ROOT_DIR)
    parser.parse_heroes()
    

