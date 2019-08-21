#!/usr/bin/env python3
import re
import yaml
from jinja2 import Environment, FileSystemLoader
from datetime import date
from pandas import read_csv

icon_conf = dict(
    url = 'https://material.io/resources/icons/static/icons',
    style = 'round',
    size = '24px',
    type = 'svg'
)
icons = {
    'experience': 'work',
    'education' : 'school',
    'info'      : 'person',
    'skills'    : 'how_to_reg',
    'project'   : 'favorite',
}

def tolevel(lvl):
    if lvl > 8:
        s = 'Expert'
    elif lvl > 6:
        s =  'Experienced'
    elif lvl > 4:
        s =  'Skillful'
    elif lvl > 2:
        s =  'Beginner'
    elif lvl > 0:
        s =  'Novice'
    else:
        s =  'None'
    return s

class Competencies(dict):
    def load(self, file):
        data = read_csv(file, sep=';', index_col=0)
        data = data.sort_values('level', ascending=False)
        data = { k:v for k,(v,) in data.T.to_dict('list').items() }
        self.update(data)
        return self

class Data(dict):

    def load(self, file):
        with open(file, 'r', encoding='UTF-8') as f:
            data = yaml.safe_load(f)
        self.update(data)
        self['age'] = self.age
        self['icon'] = self.icon
        self['highlight_skills'] = self.highlight_skills
        return self

    def highlight_skills(self, s):
        for key in self['skills']:
            s = s.replace(key, '**%s**' % key)
        return s

    def icon(self, cat):
        name = icons[cat]
        return '{url}/{style}-{name}-{size}.{type}'.format(name=name, **icon_conf) 

    @property
    def age(self):
        parts = list(map(int, self['birth']['date'].split('-')))
        birth = date(*parts[::-1])
        today = date.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day)) 

def generate():

    data = Data().load("resume.yml")
    data['skills'] = Competencies().load("competencies.txt")
        
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=FileSystemLoader('.')
    )
    template = env.get_template("resume.txt")
    md = template.render(data)

    with open('resume.md', 'w', encoding='UTF-8') as f:
        f.write(md)
        
if __name__ == '__main__':
    generate()