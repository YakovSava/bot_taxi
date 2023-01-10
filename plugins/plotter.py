import squarify
import calmap
import warnings
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

from os.path import join
from typing import Optional, Union

warnings.filterwarnings('ignore')


class Plotter:
	
	def __init__(self):
		large = 22; med = 16
		params = {'axes.titlesize': large,
				'legend.fontsize': med,
				'figure.figsize': (16, 10),
				'axes.labelsize': med,
				'axes.titlesize': med,
				'xtick.labelsize': med,
				'ytick.labelsize': med,
				'figure.titlesize': large}
		plt.rcParams.update(params)
		plt.style.use('seaborn-whitegrid')
		sns.set_style("white")

	async def _get_name(self):
		return join('cache', f'{random.randint(10000, 99999)}.png')

	async def get_area_diagramm(self, csv:Union[list, dict], time:Optional[str]) -> str:
		'''
	A hint to future developers
	The table should look like this:
	Times		Trips
0   20-12-2022  4
1   21-12-2022  1
2   22-12-2022  3
3   23-12-2022  0
4   24-12-2022  0
5   25-12-2022  0
6   26-12-2022  2
7   27-12-2022  0
		'''
		df = pd.DataFrame(csv)
		x = np.arange(df.shape[0])
		plt.figure(figsize=(16,10), dpi= 80)
		plt.fill_between(x[1:], df.trips[1:], 0, where=df.trips[1:] > 0, facecolor='green', interpolate=True, alpha=0.7)
		plt.fill_between(x[1:], df.trips[1:], 0, where=df.trips[1:] <= 0, facecolor='red', interpolate=True, alpha=0.7)
		xtickvals = [str(times) for times in df.times]
		plt.gca().set_xticks(x[::6])
		plt.gca().set_xticklabels(xtickvals[::6], rotation=90, fontdict={'horizontalalignment': 'center', 'verticalalignment': 'center_baseline'})
		plt.ylim(-35,35)
		plt.xlim(1,100)
		plt.title("Quantity of trips", fontsize=22)
		plt.ylabel('Monthly trips')
		plt.grid(alpha=0.5)
		name = await self._get_name()
		plt.savefig(name)
		return name

	async def get_sort_histogramm(self, csv:Union[list, dict]) -> str:
		'''
	Table:
	name	vk		trips
0   Igor	111		16
1 	Anna	222 	11
2 	Misha	333		9
3 	Abdul	444		5
4 	Rahman	555		2
		'''
		df = pd.DataFrame(csv)
		df.sort_values('trips', inplace=True)
		df.reset_index(inplace=True)
		fig, ax = plt.subplots(figsize=(16,10), facecolor='white', dpi= 80)
		ax.vlines(x=df.index, ymin=0, ymax=df.trips, color='firebrick', alpha=0.7, linewidth=20)
		for i, trip in enumerate(df.trips):
			ax.text(i, trip+0.5, round(trip, 1), horizontalalignment='center')
		ax.set_title('The record for the trip', fontdict={'size':22})
		ax.set(ylabel='Trips', ylim=(0, 30))
		plt.xticks(df.index, f'{df.name.str.upper()}_{df.vk.str}', rotation=60, horizontalalignment='right', fontsize=12)
		p1 = patches.Rectangle((.57, -0.005), width=.33, height=.13, alpha=.1, facecolor='green', transform=fig.transFigure)
		p2 = patches.Rectangle((.124, -0.005), width=.446, height=.13, alpha=.1, facecolor='red', transform=fig.transFigure)
		fig.add_artist(p1)
		fig.add_artist(p2)
		name = await self._get_name()
		plt.savefig(name)
		return name

	async def get_pyramid_of_gender(self, csv:Union[dict, list]) -> str:
		'''
	Table:
		stage 		gender		quantity
0 		2022-12		male		12
1 		2022-13		male 		11
2 		2022-14 	male 		7
3 		2022-12 	female		11
4 		2022-13	 	female  	12
5 		2022-14 	female  	4
		'''
		df = pd.DataFrame(csv)
		plt.figure(figsize=(13,10), dpi= 80)
		group_col = 'gender'
		order_of_bars = df.stage.unique()[::-1]
		colors = [plt.cm.Spectral(i/float(len(df[group_col].unique())-1)) for i in range(len(df[group_col].unique()))]

		for c, group in zip(colors, df[group_col].unique()):
			sns.barplot(x='quantity', y='stage', data=df.loc[df[group_col]==group, :], order=order_of_bars, color=c, label=group)
		plt.xlabel("$quantity$")
		plt.ylabel("Stage of time")
		plt.yticks(fontsize=12)
		plt.title("Population Pyramid of the drivers", fontsize=22)
		plt.legend()
		name = await self._get_name()
		plt.savefig(name)
		return name

	async def get_tree_diagram(self, csv:Union[list, dict]) -> str:
		'''
	Table:
	city	    	drivers		passangers
0 	Volgograd		5 			12
1 	Moscow			76 			97
2 	S.Pitershburg	34			12
		'''
		df = pd.DataFrame(csv)
		labels = df.apply(lambda x: f'{x[0]}\n({x[1]} - {x[2]})', axis=1)
		sizes = [a + b for a, b in zip(df['drivers'].values.tolist(), df['passangers'].values.tolist())]
		colors = [plt.cm.Spectral(i/float(len(labels))) for i in range(len(labels))]
		plt.figure(figsize=(12,8), dpi=80)
		squarify.plot(sizes=sizes, label=labels, color=colors, alpha=.8)
		plt.title('Treemap of drivers or passangers')
		plt.axis('off')
		name = await self._get_name()
		plt.savefig(name)
		return name
	
	async def get_histogram(self, csv:Union[list, dict]) -> str:
		'''
	Table
	city		 driver
0 	volgograd	 15
1 	moscow		 22
3	S.Pitersburg 11
		'''
		df = dp.DataFrame(csv)
		n = df['city'].unique().__len__()+1
		all_colors = list(plt.cm.colors.cnames.keys())
		random.seed(100)
		c = random.choices(all_colors, k=n)
		plt.figure(figsize=(16,10), dpi= 80)
		plt.bar(df['city'], df['driver'], color=c, width=.5)
		for i, val in enumerate(df['driver'].values):
			plt.text(i, val, float(val), horizontalalignment='center', verticalalignment='bottom', fontdict={'fontweight':500, 'size':12})
		plt.gca().set_xticklabels(df['city'], rotation=60, horizontalalignment = 'right')
		plt.title("Drivers in sitys", fontsize=22)
		plt.ylabel('Drivers')
		plt.ylim(0, 45)
		name = await self._get_name()
		plt.savefig(name)
		return name

	async def get_calendar_map(self, csv:Union[list, dict]) -> str:
		'''
	Table
		trips	date
0		12		12-12-2022
1 		13 		13-12-2022
2 		8		14-12-2022
		'''
		df = pd.DataFrame(csv)
		df.set_index('date', inplace=True)
		plt.figure(figsize=(16,10), dpi= 80)
		calmap.calendarplot(df['trips'], fig_kws={'figsize': (16,10)}, yearlabel_kws={'color':'black', 'fontsize':14}, subplot_kws={'title': 'Your stats'})
		name = await self._get_name()
		plt.savefig(name)
		return name

	async def get_histogram_passanger(self, csv:Union[list, dict]) -> str:
		'''
	Table
	city		 passanger
0 	volgograd	 15
1 	moscow		 22
3	S.Pitersburg 11
		'''
		df = pd.DataFrame(csv)
		n = df['city'].unique().__len__()+1
		all_colors = list(plt.cm.colors.cnames.keys())
		random.seed(100)
		c = random.choices(all_colors, k=n)
		plt.figure(figsize=(16,10), dpi= 80)
		plt.bar(df['city'], df['driver'], color=c, width=.5)
		for i, val in enumerate(df['driver'].values):
			plt.text(i, val, float(val), horizontalalignment='center', verticalalignment='bottom', fontdict={'fontweight':500, 'size':12})
		plt.gca().set_xticklabels(df['city'], rotation=60, horizontalalignment = 'right')
		plt.title("Drivers in sitys", fontsize=22)
		plt.ylabel('Drivers')
		plt.ylim(0, 45)
		name = await self._get_name()
		plt.savefig(name)
		return name