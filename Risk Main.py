from pylab import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import requests
import pandas_datareader.data as web
from Create_PDF_Report import portfolio_report

ALPHA_VANTAGE_KEY = 'ENTER_KEY'
RESULT_DETAILED = True

USER_AGENT = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
}
sesh = requests.Session()
sesh.headers.update(USER_AGENT)


def check_if_weekend(date):
    def test(date):
        try:
            temp_date = date.strftime('%Y-%m-%d')
            temp = data_set.loc[temp_date]
            error = False
        except:
            date = date - datetime.timedelta(days=1)
            error = True
        return date, error

    if date.weekday() == 6:
        date = date - datetime.timedelta(days=2)
    elif date.weekday() == 5:
        date = date - datetime.timedelta(days=1)
    try:
        temp = data_set.loc[date.strftime('%Y-%m-%d')]
        error = False
    except:
        error = True
        while error == True:
            date, error = test(date)

    return date


def calculate_return(start_date, end_date):
    global data_set
    data_set = portfolio_main.historical_performance_stock()
    portfolio_return = 0
    try:
        if data_set.all() != 0:
            end_date_value = data_set.loc[end_date]
            start_date_value = data_set.loc[start_date]
            portfolio_return += ((float(end_date_value) / float(start_date_value)) - 1) * total_hist_p_allocation
    except AttributeError:
        i = 0
    i = 0
    while i < len(ava_fund_list):
        url = "https://www.avanza.se/_api/fund-guide/chart/" + ava_fund_list_id[i] + "/" + start_date + "/" + end_date
        response = requests.get(url)
        dictr = response.json()
        recs = dictr['dataSerie']
        ava_fund_temp_data = pd.json_normalize(recs)
        performance_ava_fund = float(ava_fund_temp_data.iloc[-1, 1]) / 100 * ava_fund_list_allocation[i]
        portfolio_return += performance_ava_fund
        i += 1
    return portfolio_return


class Portfolio:

    def historical_performance_all(self):
        ava_fund = pd.read_csv('Avanza Fond ID.csv', index_col=0)
        date_list = []
        for item in self.position_performance:
            date_list.append(item.index[0])
        i_date = 0
        while date_list[i_date] != max(date_list):
            i_date += 1
        i = i_date
        if self.positions[i] not in ava_fund.index:
            temp_data = self.position_performance[i].groupby(self.position_performance[i].index.to_period('M')).first()
            temp_data = temp_data.dropna()
            temp_data.rename({'Adj Close': 'y'}, axis=1, inplace=True)
            temp_data.index.name = 'x'
            temp_data = (temp_data.div(temp_data['y'][0]) - 1) * 100
        else:
            temp_data = self.position_performance[i]
            temp_data = temp_data.groupby(temp_data.index.to_period('M')).first()

        portfolio_historical_performance = temp_data['y'] * self.position_allocation[i]
        i = 0
        i += 1
        while i < len(self.positions):
            if i != i_date:
                if self.positions[i] not in ava_fund.index:
                    temp_data = self.position_performance[i].groupby(
                        self.position_performance[i].index.to_period('M')).first()
                    temp_data = temp_data.dropna()
                    temp_data.rename({'Adj Close': 'y'}, axis=1, inplace=True)
                    temp_data.index.name = 'x'
                    temp_data = (temp_data.div(temp_data['y'][0]) - 1) * 100
                else:
                    temp_data = self.position_performance[i]
                    temp_data = temp_data.groupby(temp_data.index.to_period('M')).first()
                if portfolio_historical_performance.index[0] in temp_data.index:
                    data_point_first = int(temp_data.index.get_loc(portfolio_historical_performance.index[0]))
                    temp_data = temp_data.iloc[data_point_first:].div(temp_data.iloc[data_point_first, 0])
                    portfolio_historical_performance += temp_data['y'] * self.position_allocation[i]
                else:
                    portfolio_historical_performance += temp_data['y'] * self.position_allocation[i]
            i += 1

        # Plotting Stuff

        slower = np.ma.masked_where(portfolio_historical_performance > 0, portfolio_historical_performance)
        negative_return = portfolio_historical_performance.copy()
        negative_return[slower > 0] = np.nan
        fig, ax = plt.subplots(figsize=(10, 5))
        portfolio_historical_performance.plot(ax=ax, color="#348dc1")  # Benchmark Colour ? "#fedd78"
        negative_return.plot(ax=ax, color="darkred")
        ax.set_ylabel('', fontweight='bold', fontsize=12, color="black")
        ax.set_xlabel('')
        ax.yaxis.set_label_coords(-.1, .5)
        ax.grid(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        fig.suptitle("Performance", y=.99, fontweight="bold",
                     fontsize=14, color="black")
        ax.axhline(0, ls="-", lw=1,
                   color='gray', zorder=1)
        ax.axhline(0, ls="--", lw=1,
                   color='black', zorder=2)
        fig.set_facecolor('white')
        ax.set_title("%s - %s" % (
            portfolio_historical_performance.index[:1][0].strftime('%e %b \'%y'),
            portfolio_historical_performance.index[-1:][0].strftime('%e %b \'%y')
        ), fontsize=12, color='gray')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}%".format(int(x))))
        ax.set_facecolor('white')
        ax.fill_between(portfolio_historical_performance.index, 0, portfolio_historical_performance,
                        where=portfolio_historical_performance >= 0, interpolate=True,
                        color="#348dc1", alpha=.25)
        ax.fill_between(portfolio_historical_performance.index, 0, portfolio_historical_performance,
                        where=portfolio_historical_performance <= 0, interpolate=True,
                        color="red", alpha=.25)
        fig.autofmt_xdate()
        try:
            fig.tight_layout()
            # plt.subplots_adjust(hspace=0, bottom=0, top=1)
        except Exception:
            pass
        fig.savefig("Portfolio_Return.png")

    def historical_performance_stock(self):
        global total_hist_p_allocation
        total_hist_p_allocation = 0
        ava_fund = pd.read_csv('Avanza Fond ID.csv', index_col=0)
        if self.positions[0] not in ava_fund.index:
            performance = self.position_performance[0]['Adj Close'].div(
                self.position_performance[0]['Adj Close'][0]).dropna().mul(self.position_allocation[0])
            total_hist_p_allocation += self.position_allocation[0]
        else:
            performance = 0
        loc_perf_index = 1
        while len(self.positions) > loc_perf_index:
            if self.positions[loc_perf_index] not in ava_fund.index:
                if len(self.positions) > loc_perf_index:
                    performance += self.position_performance[loc_perf_index]['Adj Close'].div(
                        self.position_performance[loc_perf_index]['Adj Close'][0]).dropna().mul(
                        self.position_allocation[loc_perf_index])
                    total_hist_p_allocation += self.position_allocation[loc_perf_index]
            loc_perf_index += 1
        '''
        fig, ax = plt.subplots()
        ax.plot(performance, '-')
        ax.grid(True)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        fig.suptitle('Performance')
        fig.autofmt_xdate()
        plt.show()
        '''
        if total_hist_p_allocation == 0:
            performance = 0
        return performance

    def stress_test(self):
        draw_downs = 'Drawback Periods:\n\nGlobal Financial Crisis (10.09.2007-03.09.2009)\nPerformance: ' + str(round(
            calculate_return("2007-10-09", "2009-03-09") * 100,
            2)) + '%  SP500: -54.89%\nU.S. Downgrade (04.30.2011-10.03.2011)\nPerformance: ' + str(round(
            calculate_return("2011-04-29", "2011-10-03") * 100,
            2)) + '%  SP500: -18.64%\nGlobal Slowdown Fears (05.22.2015-08.25.2015)\nPerformance: ' + str(round(
            calculate_return("2015-05-22", "2015-08-25") * 100,
            2)) + '%  SP500: -11.89%\nOil, U.S. Recession Fears (11.04.2015-02.11.2016)\nPerformance: ' + str(round(
            calculate_return("2015-11-04", "2016-02-11") * 100,
            2)) + '%  SP500: -12.71%\nRising Rates/Trade (09.21.2018-12.24.2018) \nPerformance: ' + str(round(
            calculate_return("2018-09-21", "2018-12-24") * 100,
            2)) + '%  SP500: -19.36%\nCovid-19 Concerns Begin (02.19.2020-03.23.2020) \nPerformance: ' + str(round(
            calculate_return("2020-02-19", "2020-03-23") * 100, 2)) + '%  SP500: -33.47%'

        rebounds = 'Rebound Periods:\n\nRecession Ends (03.10.2009-04.23.2010)\nPerformance: ' + str(round(
            calculate_return("2009-03-10", "2010-04-23") * 100,
            2)) + '%  SP500: 84.21%\nFlash Crash Rebound/European Relief (07.02.2010-02.18.2011)\nPerformance: ' + str(
            round(
                calculate_return("2010-07-02", "2011-02-18") * 100,
                2)) + '%  SP500: 33.02%\nCentral Bank QE (12.30.2011-12.29.2014)\nPerformance: ' + str(round(
            calculate_return("2011-12-30", "2014-12-29") * 100,
            2)) + '%  SP500: 55.40%\nChina Easing/Oil rebound/Weaker USD (02.12.2016-01.26.2018)\nPerformance: ' + str(
            round(
                calculate_return("2016-02-12", "2018-01-26") * 100,
                2)) + '%  SP500: 63.49%\nFed Eases (12.26.2018-12.27.2019)\nPerformance: ' + str(round(
            calculate_return("2018-12-26", "2019-12-27") * 100,
            2)) + '%  SP500: 40.63%\nFiscal/Fed Covid-19 Response (03.24.2020-06.08.2020)\nPerformance: ' + str(round(
            calculate_return("2020-03-24", "2020-06-08") * 100, 2)) + '%  SP500: 40.63%'

        falling_ir = 'Falling Interest Rates:\n\nU.S. Downgrade (02.09.2011-09.22.2011)\nPerformance: ' + str(round(
            calculate_return("2011-02-09", "2011-09-22") * 100,
            2)) + '%  (-2.03)\nEurope Debt Crisis/Flight to Quality (03.20.2012-07.25.2012)\nPerformance: ' + str(round(
            calculate_return("2012-03-20", "2012-07-25") * 100,
            2)) + '%  (-0.93)\nWeaker Growth/Low Inflation (01.09.2014-02.02.2015)\nPerformance: ' + str(round(
            calculate_return("2014-01-09", "2015-02-02") * 100,
            2)) + '%  (-1.33)\nGlobal Slowdown Fear (06.11.2015-07.05.2016)\nPerformance: ' + str(round(
            calculate_return("2015-06-11", "2016-07-05") * 100,
            2)) + '%  (-1.13)\nEscalated U.S.-China Trade War (11.09.2018-09.04.2019)\nPerformance: ' + str(round(
            calculate_return("2018-11-09", "2019-09-04") * 100,
            2)) + '%  (-1.77)\nCovid-19 Concerns Begin (01.21.2020-03.09.2020)\nPerformance: ' + str(round(
            calculate_return("2020-01-21", "2020-03-09") * 100, 2)) + '%  (-1.30)'

        rising_ir = 'Rising Interest Rates (Change in RFR)\n\n10.06.2010-02.08.2011\nPerformance: ' + str(round(
            calculate_return("2010-10-06", "2011-08-02") * 100,
            2)) + '%  (+1.34)\n05.02.2013-09.05.2013\nPerformance: ' + str(round(
            calculate_return("2013-05-02", "2013-09-05") * 100,
            2)) + '%  (+1.32)\n07.08.2015-12.15.2015\nPerformance: ' + str(round(
            calculate_return("2015-07-08", "2015-12-15") * 100,
            2)) + '%  (+1.23)\n09.07.2017-05.17.2018\nPerformance: ' + str(round(
            calculate_return("2017-09-07", "2018-05-17") * 100,
            2)) + '%  (+1.06)\nCovid-19 Recovery/Inflation Concerns (03.09.2020-03.19.2021)\nPerformance: ' + str(round(
            calculate_return("2020-03-09", "2021-03-19") * 100, 2)) + '%  (+1.20)'

        return draw_downs, rebounds, falling_ir, rising_ir

    def pdf_data_generate(self):
        ava_fund = pd.read_csv('Avanza Fond ID.csv', index_col=0)
        today = datetime.datetime.now()
        today_date = check_if_weekend(today)
        today_date = today_date.strftime('%Y-%m-%d')

        date_one_y_ago = today - datetime.timedelta(days=365)
        date_one_y_ago = check_if_weekend(date_one_y_ago)
        date_one_y_ago = date_one_y_ago.strftime('%Y-%m-%d')
        date_one_m_ago = today - datetime.timedelta(days=30)
        date_one_m_ago = check_if_weekend(date_one_m_ago)
        date_one_m_ago = date_one_m_ago.strftime('%Y-%m-%d')
        date_three_m_ago = today - datetime.timedelta(days=90)
        date_three_m_ago = check_if_weekend(date_three_m_ago)
        date_three_m_ago = date_three_m_ago.strftime('%Y-%m-%d')
        date_three_y_ago = today - datetime.timedelta(days=1095)
        date_three_y_ago = check_if_weekend(date_three_y_ago)
        date_three_y_ago = date_three_y_ago.strftime('%Y-%m-%d')
        date_begin_of_year = today.date().replace(month=1, day=1)
        date_begin_of_year = check_if_weekend(date_begin_of_year)
        date_begin_of_year = date_begin_of_year.strftime('%Y-%m-%d')

        performance_1m = str(round(calculate_return(date_one_m_ago, today_date) * 100, 2))
        performance_3m = str(round(calculate_return(date_three_m_ago, today_date) * 100, 2))
        performance_ytd = str(round(calculate_return(date_begin_of_year, today_date) * 100, 2))
        performance_1y = str(round(calculate_return(date_one_y_ago, today_date) * 100, 2))
        performance_3y = str(round(calculate_return(date_three_y_ago, today_date) * 100, 2))
        i_ava = 0
        i = 0
        holding_overview_list = []
        for position in positions_list:
            position_current_list = []
            position_current_list.append(position)
            data_frame_temp = self.position_performance[i]
            if position not in ava_fund.index:
                performance_current_1y = str(round((float(data_frame_temp['Adj Close'][-1]) / float(
                    data_frame_temp['Adj Close'].loc[date_one_y_ago]) - 1) * 100, 2)) + "%"
                performance_current_3y = str(round((float(data_frame_temp['Adj Close'][-1]) / float(
                    data_frame_temp['Adj Close'].loc[date_three_y_ago]) - 1) * 100, 2)) + "%"
            else:
                json_dict = ava_fund_list_info[i_ava]
                try:
                    performance_current_1y = str(round(json_dict['developmentOneYear'], 2)) + "%"
                    performance_current_3y = str(round(json_dict['developmentThreeYears'], 2)) + "%"
                except:
                    performance_current_1y = 'Error'
                    performance_current_3y = 'Error'
                i_ava += 1
            position_current_list.append(performance_current_1y)
            position_current_list.append(performance_current_3y)
            position_current_list.append(str(self.position_allocation[i] * 100) + "%")

            holding_overview_list.append(position_current_list)

            i += 1

        return performance_1m, performance_3m, performance_ytd, performance_1y, performance_3y, holding_overview_list

    def __init__(self, list_of_positions, allocation_of_positions):  # initalized function
        self.positions = list_of_positions
        self.position_allocation = allocation_of_positions

        global ava_fund_list, ava_fund_list_info, ava_fund_list_allocation, ava_fund_list_id, in_ava_fund, stock_details, stock_overview, stock_ratings, stock_forecast

        position_data_frame_list = []
        ava_fund_list = []
        ava_fund_list_info = []
        ava_fund_list_allocation = []
        ava_fund_list_id = []
        in_ava_fund = []
        stock_details = []
        stock_temp = []
        stock_overview = []
        stock_ratings = []
        stock_forecast = []

        ava_fund = pd.read_csv('Avanza Fond ID.csv', index_col=0)

        while len(self.positions) > len(position_data_frame_list):
            if self.positions[len(position_data_frame_list)] in ava_fund.index:
                fund_id = ava_fund.loc[self.positions[len(position_data_frame_list)], 'ID']
                url = 'https://www.avanza.se/_api/fund-guide/guide/' + fund_id
                response = requests.get(url)

                ava_fund_list.append(self.positions[len(position_data_frame_list)])
                ava_fund_list_id.append(fund_id)
                ava_fund_list_info.append(response.json())
                ava_fund_list_allocation.append(self.position_allocation[len(position_data_frame_list)])

                url = 'https://www.avanza.se/_api/fund-guide/chart/' + fund_id + '/infinity'
                response = requests.get(url)
                dictr = response.json()
                recs = dictr['dataSerie']
                temp_data = pd.json_normalize(recs)
                i = 0
                for item in temp_data['x']:
                    test = datetime.datetime.fromtimestamp(int(float(item) / 1000))
                    temp_data.iloc[i, 0] = f"{test:%Y-%m-%d}"
                    i += 1
                temp_data['x'] = pd.to_datetime(temp_data['x'])
                temp_data = temp_data.set_index('x')
                # temp_data = temp_data.groupby(temp_data.index.to_period('M')).first()
                temp_data = temp_data.dropna()
                position_data_frame_list.append(temp_data)
                in_ava_fund.append(True)
                stock_details.append(0)
                stock_overview.append(0)
                stock_ratings.append(0)
                stock_forecast.append(0)
            else:
                if RESULT_DETAILED:
                    '''Get Alpha Vantage Data'''
                    url = 'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={}&apikey={}'.format(
                        self.positions[len(position_data_frame_list)],
                        ALPHA_VANTAGE_KEY)
                    response = requests.get(url)
                    dictr = response.json()
                    stock_temp.append(pd.json_normalize(dictr['quarterlyReports']))
                    stock_temp.append(pd.json_normalize(dictr['annualReports']))

                    url = 'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={}&apikey={}'.format(
                        self.positions[len(position_data_frame_list)],
                        ALPHA_VANTAGE_KEY)
                    response = requests.get(url)
                    dictr = response.json()
                    stock_temp.append(pd.json_normalize(dictr['quarterlyReports']))
                    stock_temp.append(pd.json_normalize(dictr['annualReports']))

                    url = 'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={}&apikey={}'.format(
                        self.positions[len(position_data_frame_list)],
                        ALPHA_VANTAGE_KEY)
                    response = requests.get(url)
                    dictr = response.json()
                    stock_temp.append(pd.json_normalize(dictr['quarterlyReports']))
                    stock_temp.append(pd.json_normalize(dictr['annualReports']))

                    url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol={}&apikey={}'.format(
                        self.positions[len(position_data_frame_list)],
                        ALPHA_VANTAGE_KEY)
                    response = requests.get(url)
                    stock_overview.append(response.json())

                    url = "https://api.nasdaq.com/api/analyst/" + self.positions[len(position_data_frame_list)] + "/ratings"
                    response = requests.get(url, headers=USER_AGENT)
                    stock_ratings.append(response.json())

                    url = "https://api.nasdaq.com/api/analyst/" + self.positions[len(position_data_frame_list)] + "/earnings-forecast"
                    response = requests.get(url, headers=USER_AGENT)
                    stock_forecast.append(stock_temp)

                    stock_details.append(stock_temp)

                position_data_frame_list.append(web.DataReader(self.positions[len(position_data_frame_list)], 'yahoo',
                                                               start=datetime.datetime(2000, 1, 1),
                                                               end=datetime.date.today(), session=sesh))

                in_ava_fund.append(False)
        self.position_performance = position_data_frame_list


positions_list = []
position_size_list = []
positions = int(input('Enter Number of positions: '))

while positions > 0:
    positions_list.append(input('Enter Position: '))
    position_size_list.append(int(input('Enter Position Allocation in %: ')) / 100)
    positions -= 1

portfolio_main = Portfolio(positions_list, position_size_list)
draw_downs, rebounds, falling_ir, rising_ir = portfolio_main.stress_test()
portfolio_main.historical_performance_all()
performance_1m, performance_3m, performance_ytd, performance_1y, performance_3y, holding_overview_list = portfolio_main.pdf_data_generate()

portfolio_report(draw_downs, rebounds, falling_ir, rising_ir, performance_1m, performance_3m, performance_ytd,
                 performance_1y, performance_3y, holding_overview_list, in_ava_fund, ava_fund_list_info, stock_details, stock_overview, positions_list, stock_ratings)
