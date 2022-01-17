# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import csv
import math

#read in data
playbyplay = pd.read_csv('NBA_PBP_2015-16.csv')
#no playoff data
playbyplay = playbyplay.loc[playbyplay['GameType'] == 'regular']
#need just fouls and freethrows
fouls_and_freethrows = playbyplay.loc[(playbyplay['FoulType'].notnull()) | (playbyplay['FreeThrowOutcome'].notnull()),
                                      ['Quarter', 'SecLeft', 'AwayTeam', 'AwayPlay', 'AwayScore', 'HomeTeam', 'HomePlay',
                                       'HomeScore', 'FoulType', 'Fouler', 'Fouled', 'FreeThrowShooter', 'FreeThrowOutcome',
                                       'FreeThrowNum']]
