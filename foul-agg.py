# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import csv
import math
import dataframe_image as dfi
import seaborn as sb
import matplotlib.pyplot as plt

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
#bringing it together
new_df = pd.merge(fouls, pd.merge(num_ft.rename('num_ft'), mft1, on=['URL', 'Quarter', 'SecLeft']), on=['URL', 'Quarter', 'SecLeft'])
total = new_df.rename(columns={'0': 'num_ft'})
total = total.drop(['FreeThrowOutcome', 'FreeThrowNum'], axis=1)
#good fouls
conditions = [
    ((total['made_ft'] < total['num_ft']) & (total['num_ft'] == 2)),
]

total['good_foul'] = np.where(conditions[0], 1, 0)
#percentage of fouls that are good (two point shot and they make less than two fts)
player_fouls = total[['Fouler']].groupby('Fouler').size()
good_fouls = total[['Fouler', 'good_foul']].groupby('Fouler').sum()

players = pd.merge(player_fouls.rename('total_fouls'), good_fouls, on=['Fouler'])
players['good_foul_pct'] = players['good_foul']/players['total_fouls']

# points saved
league_3pt_perc = {}
league_3pt_perc['15-16'] = .356
league_2pt_perc = {}
league_2pt_perc['15-16'] = .485

total['expected_pts_saved'] = np.where(total['num_ft'] == 0, 0, np.where(total['num_ft'] == 1, 0 - total['made_ft'], np.where(total['num_ft'] == 2, league_2pt_perc['15-16']*2 - total['made_ft'], np.where(total['num_ft'] == 3, league_3pt_perc['15-16']*3 - total['made_ft'], 0))))
exp_pts_saved = total[['Fouler', 'expected_pts_saved']].groupby('Fouler').sum()

total['max_possible_pts_saved'] = np.where(total['num_ft'] == 0, 0, np.where(total['num_ft'] == 1, 0 - total['made_ft'], np.where(total['num_ft'] == 2, 2 - total['made_ft'], np.where(total['num_ft'] == 3, 3 - total['made_ft'], 0))))
max_possible_pts_saved = total[['Fouler', 'max_possible_pts_saved']].groupby('Fouler').sum()

total['min_possible_pts_saved'] = np.where(total['num_ft'] == 0, 0, np.where(total['num_ft'] == 1, 0 - total['made_ft'], np.where(total['num_ft'] == 2, 0 - total['made_ft'], np.where(total['num_ft'] == 3, 0 - total['made_ft'], 0))))
min_possible_pts_saved = total[['Fouler', 'min_possible_pts_saved']].groupby('Fouler').sum()

players = pd.merge(players, pd.merge(exp_pts_saved, pd.merge(max_possible_pts_saved, min_possible_pts_saved, on=['Fouler']), on=['Fouler']), on=['Fouler'])
players = players.loc[players['total_fouls'] >= 20]

players['expected_pts_saved/good_foul'] = players['expected_pts_saved']/players['good_foul']

#players.sort_values(by=['expected_pts_saved/good_foul'], inplace=True, ascending=False)
players.sort_values(by=['total_fouls'], inplace=True, ascending=False)
players = players.reset_index()

#dfi.export(players, 'nba-fouls.png', max_rows=-1)

fig, ax = plt.subplots()
sb.set_style("darkgrid")
sb.scatterplot(data=players, x='expected_pts_saved/good_foul', y='good_foul_pct')
ax.set_title('Expected Points Saved per Good Foul vs Good Foul Pct')
ax.set_xlabel("Expected Points Saved per Good Foul")
ax.set_ylabel("Good Foul Pct")

plt.savefig('expected-pts-saved/good-foul-vs-good-foul-pct-2015-16.png')

#incorporate score and other aspects down here i.e. time left