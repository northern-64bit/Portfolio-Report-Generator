from fpdf import FPDF
from tabulate import tabulate
import matplotlib.pyplot as plt


# import pyPdf

sector_dict = {"Industri": "Industry",
               "Konsument, cyklisk": "Consumer goods, cyclical",
               "Finans": "Finance",
               "Konsument, stabil": "Consumer goods, stable",
               "Sjukvård": "Health Care",
               "Teknik": "Technology",
               "Fastigheter": "Real Estate",
               "Råvaror": "Commodities",
               "Kommunikation": "Telecommunication",
               "Allmännyttigt": "Utilities",
               "Energi": "Energy"}

class PDF(FPDF):
    def lines(self):
        self.set_fill_color(106.0, 130.0, 82.0)  # color for outer rectangle
        self.rect(5.0, 5.0, 200.0, 287.0, 'DF')
        self.set_fill_color(255, 255, 255)  # color for inner rectangle
        self.rect(8.0, 8.0, 194.0, 281.0, 'FD')

    def imagex(self):
        self.set_xy(8.5, 8.5)
        self.image('TA Stock System.png', link='', type='', w=1068 / 48, h=654 / 48)

    def titles(self, text, x, y):
        self.set_xy(x, y)
        self.set_font('Arial', '', 16)
        self.set_text_color(0, 0, 0)
        self.cell(w=210.0, h=40.0, align='C', txt=text, border=0, ln=1)

    def header(self):
        PDF.lines(self)
        PDF.imagex(self)
        self.ln(2)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # helvetica italic 8
        self.set_font('helvetica', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def asset_title(self, num, label):
        # helvetica 12
        self.set_font('helvetica', '', 12)
        # Background color
        self.set_fill_color(225, 225, 225)
        # Title
        self.cell(0, 6, f'Part {num} : {label}', 0, 1, 'L', True)
        # Line break
        self.ln()

    def fancy_table(self, header, data, position_x, w, position_y=0):
        # Colors, line width and bold font
        self.set_fill_color(106.0, 130.0, 82.0)
        self.set_text_color(255)
        self.set_draw_color(225, 225, 225)
        self.set_line_width(0.3)
        self.set_font('helvetica', style="B", size=6)
        # Header

        if position_y != 0:
            self.set_xy(position_x, position_y)
        else:
            self.set_x(position_x)
        for width, header_text in zip(w, header):
            self.cell(width, 7, header_text, 1, 0, "C", True)
        self.ln()
        # Color and font restoration
        self.set_fill_color(200, 200, 200)
        self.set_text_color(0)
        self.set_font('helvetica', '', 5)
        # Data
        fill = False
        for row in data:
            if position_y != 0:
                position_y += 6
                self.set_xy(position_x, position_y)
            else:
                self.set_x(position_x)
            self.cell(w[0], 6, row[0], "LR", 0, "L", fill)
            if len(header) > 1:
                self.cell(w[1], 6, row[1], "LR", 0, "L", fill)
            if len(header) > 2:
                self.cell(w[2], 6, row[2], "LR", 0, "R", fill)
            if len(header) > 3:
                self.cell(w[3], 6, row[3], "LR", 0, "R", fill)
            if len(header) > 4:
                self.cell(w[4], 6, row[4], "LR", 0, "R", fill)
            if len(header) > 5:
                self.cell(w[5], 6, row[5], "LR", 0, "R", fill)
            self.ln()
            fill = not fill
        self.set_x(position_x)
        self.cell(sum(w), 0, "", "T")

    def overview_content(self, header, data):
        self.set_font('helvetica', 'B', 8)
        self.fancy_table(header, data, 145, [25, 25])
        self.ln(4)
        img_size_width = 130
        self.image('Portfolio_Return.png', x=10, y=50, w=img_size_width, h=int(img_size_width / 2))

    def stress_test(self, column1, column2, column3, column4):
        self.set_font('helvetica', '', 6)
        self.multi_cell(txt=column1, w=0)
        self.set_xy(60, 126)
        self.multi_cell(txt=column2, w=0)
        self.set_xy(125, 126)
        self.multi_cell(txt=column3, w=0)
        self.ln(8)
        self.multi_cell(txt=column4, w=0)

    def holdings(self, header, data):
        self.ln()
        self.fancy_table(header, data, 10, [50, 25, 25, 25])

    def detailed_position_information(self, positions, in_ava_fund, ava_fund_list_info, stock_details, stock_overview, stock_ratings):
        self.ln(3)
        i_name_num = 4.1
        i = 0
        i_ava = 0
        i_stock_detailed = 1
        details_start = 0
        details_end = 5
        details_labels = ["Balance Sheet Quarterly", "Balance Sheet Annually", "Cah Flow Quarterly",
                          "Cash Flow Annually", "Income Statement Quarterly", "Income Statement Annually"]
        for position in positions:
            self.asset_title(i, position)
            self.ln(2)
            self.set_font('helvetica', '', 6)
            i_name_num += 0.1
            if in_ava_fund[i]:
                current_data = ava_fund_list_info[i_ava]
                text = "Swedish Description:\n\n" + current_data['description'] + "\n\nThe fund is managed by:\n"
                for manager in current_data['fundManagers']:
                    text = text + "\t- " + manager['name'] + " since " + manager['startDate'] + '\n'
                text = (text + "from " + current_data['adminCompany']['name'] + ". The currency of the fund is " +
                        current_data['currency'] + " and it the fund started " + current_data['startDate']) + "."
                if current_data['indexFund']:
                    text = text + " It is a index fund."
                else:
                    text = text + " It is not a index fund."
                text = (text + " The fund manages " + str(current_data['capital']) + current_data['currency'] + ". The "
                        "standard deviation of the fund is " + str(current_data['standardDeviation']) + " and the sharpe "
                        "ratio is " + str(current_data['sharpeRatio']) + ".")

                self.multi_cell(txt=text, w=0)
                table_row = []
                self.ln()
                for data in current_data['countryChartData']:
                    table_row_temp = []
                    table_row_temp.append(data['countryCode'])
                    table_row_temp.append(str(data['y']))
                    table_row.append(table_row_temp)
                header = ["Country", "Allocation in %"]
                self.fancy_table(header, table_row, 10, [10, 18], 80)
                table_row = []
                for data in current_data['holdingChartData']:
                    table_row_temp = []
                    table_row_temp.append(data['name'])
                    table_row_temp.append(str(data['y']))
                    table_row_temp.append(data['countryCode'])
                    table_row.append(table_row_temp)
                header = ["Holding", "Allocation in %", "Country"]
                self.fancy_table(header, table_row, 45, [40, 25, 15], 80)
                table_row = []
                for data in current_data['sectorChartData']:
                    table_row_temp = []
                    table_row_temp.append(sector_dict[data['name']])
                    table_row_temp.append(str(data['y']))
                    table_row.append(table_row_temp)
                header = ["Sector (SE)", "Allocation in %"]
                self.fancy_table(header, table_row, 135, [25, 25], 80)
                i_ava += 1
                self.ln(60)
            else:
                self.set_font('helvetica', '', 4)
                current_data = stock_overview[i]
                text = current_data['Description'] + "\nIt's in the " + current_data['Industry'].lower() + " industry (" \
                       + current_data['Sector'].lower() + " sector). The stock has a market cap of " + \
                       current_data['MarketCapitalization'] + " with a P/E-ratio of " + current_data['PERatio'] + \
                       ", P/B-ratio of " + current_data['PriceToBookRatio'] + " and a dividend yield of " + \
                       current_data['DividendYield'] + ". Institutions own " + current_data['PercentInstitutions'] + "% and insiders " + current_data['PercentInsiders'] + "% of the shares.\n\n"
                current_data = stock_ratings[i]
                current_data = current_data['data']
                text += "Analyst ratings:\n" + current_data['meanRatingType'] + " " \
                        + current_data['ratingsSummary'] + " The ratings are from: "
                for broker in current_data['brokerNames']:
                    text += broker + "; "
                text += "\n\n"
                current_data = stock_details[i]
                while details_start < details_end:
                    df_detailed = current_data[i_stock_detailed].transpose()
                    text += details_labels[i_stock_detailed] + ": \n" + tabulate(df_detailed, headers=df_detailed.columns, showindex="always") + '\n\n'
                    i_stock_detailed += 2
                    details_start += 2
                details_start = 0
                i_stock_detailed = 1
                self.multi_cell(txt=text, w=0)
                self.ln(2)

                # Balance Sheet Overview
                total_assets = stock_details[i][1]['totalAssets']
                total_assets = list(map(int, total_assets))
                total_liabilities = stock_details[i][1]['totalLiabilities']
                total_liabilities = list(map(int, total_liabilities))
                intangible_assets = stock_details[i][1]['intangibleAssets']
                intangible_assets = list(map(int, intangible_assets))
                goodwill = stock_details[i][1]['goodwill']
                goodwill = list(map(int, goodwill))

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(stock_details[i][1]['fiscalDateEnding'], total_assets, label='Balance Sheets')
                ax.plot(stock_details[i][1]['fiscalDateEnding'], total_liabilities, label='Total Liabilities')
                ax.plot(stock_details[i][1]['fiscalDateEnding'], intangible_assets, label='Intangible Assets')
                ax.plot(stock_details[i][1]['fiscalDateEnding'], goodwill, label='Goodwill')
                fig.suptitle('Balance Sheets')
                ax.grid(True)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.axhline(0, ls="-", lw=1,
                           color='gray', zorder=1)
                ax.axhline(0, ls="--", lw=1,
                           color='black', zorder=2)
                fig.set_facecolor('white')
                fig.autofmt_xdate()
                fig.legend()
                try:
                    fig.tight_layout()
                    # plt.subplots_adjust(hspace=0, bottom=0, top=1)
                except Exception:
                    pass
                fig.savefig('balance_sheet_' + position + '.png')

                # Income Statement
                total_revenue = stock_details[i][5]['totalRevenue']
                total_revenue = list(map(int, total_revenue))
                operating_income = stock_details[i][5]['operatingIncome']
                try:
                    operating_income = list(map(int, operating_income))
                except:
                    operating_income_new = []
                    operating_income = list(map(str, operating_income))
                    for item in operating_income:
                        try:
                            operating_income_new.append(int(item))
                        except:
                            operating_income_new.append(item)
                    operating_income = operating_income_new
                r_and_d = stock_details[i][5]['researchAndDevelopment']
                try:
                    r_and_d = list(map(int, r_and_d))
                except:
                    r_and_d_new = []
                    r_and_d = list(map(str, r_and_d))
                    for item in r_and_d:
                        try:
                            r_and_d_new.append(int(item))
                        except:
                            r_and_d_new.append(item)
                    r_and_d = r_and_d_new
                ebit = stock_details[i][5]['ebit']
                ebit = list(map(int, ebit))
                net_income = stock_details[i][5]['netIncome']
                net_income = list(map(int, net_income))

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(stock_details[i][5]['fiscalDateEnding'], total_revenue, label='Total Revenue')
                ax.plot(stock_details[i][5]['fiscalDateEnding'], operating_income, label='Operating Income')
                ax.plot(stock_details[i][5]['fiscalDateEnding'], r_and_d, label='R&D')
                ax.plot(stock_details[i][5]['fiscalDateEnding'], ebit, label='EBIT')
                ax.plot(stock_details[i][5]['fiscalDateEnding'], net_income, label='Net Income')
                fig.suptitle('Income Statement')
                ax.grid(True)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.axhline(0, ls="-", lw=1,
                           color='gray', zorder=1)
                ax.axhline(0, ls="--", lw=1,
                           color='black', zorder=2)
                fig.set_facecolor('white')
                fig.autofmt_xdate()
                fig.legend()
                try:
                    fig.tight_layout()
                    # plt.subplots_adjust(hspace=0, bottom=0, top=1)
                except Exception:
                    pass
                fig.savefig('income_statement_' + position + '.png')

                # Cash Flow Statement
                operating_cashflow = stock_details[i][3]['operatingCashflow']
                try:
                    operating_cashflow = list(map(int, operating_cashflow))
                except:
                    operating_cashflow_new = []
                    operating_cashflow = list(map(str, operating_cashflow))
                    for item in operating_cashflow:
                        try:
                            operating_cashflow_new.append(int(item))
                        except:
                            operating_cashflow_new.append(item)
                    operating_cashflow = operating_cashflow_new
                depreciation_depletion_amortization = stock_details[i][3]['depreciationDepletionAndAmortization']
                depreciation_depletion_amortization = list(map(int, depreciation_depletion_amortization))
                dividend_payout = stock_details[i][3]['dividendPayout']
                try:
                    dividend_payout = list(map(int, dividend_payout))
                except:
                    dividend_payout_new = []
                    dividend_payout = list(map(dividend_payout))
                    for item in dividend_payout:
                        try:
                            dividend_payout_new.append(int(item))
                        except:
                            dividend_payout_new.append(item)
                    dividend_payout = dividend_payout_new
                repurchase_equity = stock_details[i][3]['paymentsForRepurchaseOfEquity']
                try:
                    repurchase_equity = list(map(int, repurchase_equity))
                except:
                    repurchase_equity_new = []
                    repurchase_equity = list(map(str, repurchase_equity))
                    for item in repurchase_equity:
                        try:
                            repurchase_equity_new.append(int(item))
                        except:
                            repurchase_equity_new.append(item)
                    repurchase_equity = repurchase_equity_new
                net_income = stock_details[i][3]['netIncome']
                net_income = list(map(int, net_income))

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(stock_details[i][3]['fiscalDateEnding'], operating_cashflow, label='Operating Cash Flow')
                ax.plot(stock_details[i][3]['fiscalDateEnding'], depreciation_depletion_amortization, label='Depreciation, Depletion and Amortization')
                ax.plot(stock_details[i][3]['fiscalDateEnding'], dividend_payout, label='Dividend Payout')
                ax.plot(stock_details[i][3]['fiscalDateEnding'], repurchase_equity, label='Payments for repurchase of Equity')
                fig.suptitle('Cash Flow Statement')
                ax.grid(True)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.axhline(0, ls="-", lw=1,
                           color='gray', zorder=1)
                ax.axhline(0, ls="--", lw=1,
                           color='black', zorder=2)
                fig.set_facecolor('white')
                fig.autofmt_xdate()
                fig.legend()
                try:
                    fig.tight_layout()
                    # plt.subplots_adjust(hspace=0, bottom=0, top=1)
                except Exception:
                    pass
                fig.savefig('cashflow_statement_' + position + '.png')

                img_size_width = 100
                self.image('balance_sheet_'+position+'.png', x=100, y=50, w=img_size_width, h=int(img_size_width / 2))
                self.image('cashflow_statement_' + position + '.png', x=100, y=105, w=img_size_width, h=int(img_size_width / 2))
                self.image('income_statement_' + position + '.png', x=100, y=160, w=img_size_width, h=int(img_size_width / 2))
            self.add_page()
            i += 1


def portfolio_report(draw_downs, rebounds, falling_interest_r, rising_interest_r, performance_1m, performance_3m,
                     performance_ytd, performance_1y, performance_3y, holdings_overview_list, in_ava_fund,
                     ava_fund_list_info, stock_details, stock_overview, positions_list, stock_ratings):
    pdf = PDF()
    pdf.add_page()
    pdf.titles('Portfolio Report', 0, 0)
    pdf.asset_title(1, 'Overview')
    pdf.overview_content(["Timeperiod:", "Return in %:"],
                         [["1m", performance_1m], ["3m", performance_3m], ["YTD", performance_ytd],
                          ["1y", performance_1y], ["3y", performance_3y]])
    pdf.ln(22)
    pdf.asset_title(2, 'Stress Test')
    pdf.stress_test(draw_downs, rebounds, falling_interest_r, rising_interest_r)
    pdf.ln(5)
    pdf.asset_title(3, 'Holdings')
    pdf.holdings(['Positions', '1y Return', '3y Return', 'Allocation'], holdings_overview_list)
    pdf.add_page()
    pdf.asset_title(4, 'Detailed Position Information')
    pdf.detailed_position_information(positions_list, in_ava_fund, ava_fund_list_info, stock_details, stock_overview, stock_ratings)
    pdf.set_author('Autogenerated by TA Stock System Risk Software')
    pdf.output('Portfolio Report.pdf', 'F')
