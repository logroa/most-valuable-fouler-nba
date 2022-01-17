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
                                      ['URL', 'Quarter', 'SecLeft', 'AwayTeam', 'AwayPlay', 'AwayScore', 'HomeTeam', 'HomePlay',
                                       'HomeScore', 'FoulType', 'Fouler', 'Fouled', 'FreeThrowShooter', 'FreeThrowOutcome',
                                       'FreeThrowNum']]
instances = fouls_and_freethrows.groupby(['URL', 'Quarter', 'SecLeft'])
#fouls
fouls = instances.first()
#made free throws
fouls_and_freethrows['made_ft'] = np.where(fouls_and_freethrows['FreeThrowOutcome'] == 'make', 1, 0)
mft = fouls_and_freethrows[['URL', 'Quarter', 'SecLeft', 'made_ft']]
mft1 = mft.groupby(['URL', 'Quarter', 'SecLeft']).sum()
#num free throws
num_ft = fouls_and_freethrows.groupby(['URL', 'Quarter', 'SecLeft']).size() - 1
#
new_df = pd.merge(fouls, pd.merge(num_ft.rename('num_ft'), mft1, on=['URL', 'Quarter', 'SecLeft']), on=['URL', 'Quarter', 'SecLeft'])
total = new_df.rename(columns={'0': 'num_ft'})
