import json
import logging
import os

import interactions


class JSONDatabase():
    def __init__(self, player: interactions.Member, guild_id):
        self.player = player
        self.guild_id = int(guild_id)
        self.data = {}
        # update username and server everytime player is accessed
        self.data['name'] = str(self.player.user.username)
        self.data['server'] = self.guild_id
        # create records for new player
        if not self.exists():
            self.data['records'] = {}
            self.save()

    def load(self):
        if not os.path.exists(os.path.dirname(__file__) + f'/data/'):
            os.makedirs(os.path.dirname(__file__) + f'/data/')
        try:
            with open(os.path.dirname(__file__) + f'/data/{self.player.user.id}.json') as f:
                self.data = json.load(f)
        except FileNotFoundError as error:
            logging.error(
                f"{self.player.nick} does not have a record.")
            raise

    def save(self):
        if not os.path.exists(os.path.dirname(__file__) + f'/data/'):
            os.makedirs(os.path.dirname(__file__) + f'/data/')
        with open(os.path.dirname(__file__) + f'/data/{self.player.user.id}.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    def delete(self):
        os.remove(os.path.dirname(__file__) +
                  f'/data/{self.player.user.id}.json')

    def exists(self):
        return os.path.exists(os.path.dirname(__file__) + f'/data/{self.player.user.id}.json')

    @property
    def name(self):
        self.load()
        return self.data['name']

    @name.setter
    def name(self, name):
        self.load()
        self.data['name'] = name
        self.save()

    @property
    def id(self):
        self.load()
        return self.data['id']

    @id.setter
    def id(self, id):
        self.load()
        self.data['id'] = id
        self.save()

    @property
    def server(self):
        self.load()
        return self.data['server']

    @server.setter
    def server(self, server):
        self.load()
        self.data['server'] = server
        self.save()

    @property
    def records(self):
        self.load()
        return self.data['records']

    @records.setter
    def records(self, records):
        self.load()
        self.data['records'] = records
        self.save()

    def add_record(self, map, time):
        self.load()
        if map not in self.records.keys():
            self.records[map] = [time]
        else:
            self.records[map].append(time)
        self.save()

    def leaderboard(self, map, local):
        statlist = {}
        for file in os.listdir(os.path.dirname(__file__) + f'/data/'):
            with open(os.path.dirname(__file__) + f'/data/{file}') as f:
                runs = json.load(f)
            if map in runs['records'].keys():
                if local and runs['server'] != self.guild_id:
                    continue
                statlist[runs['name']] = min(runs['records'][map])
        return sorted(statlist.items(), key=lambda x: x[1])

