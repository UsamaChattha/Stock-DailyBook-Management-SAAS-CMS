from fpdf import FPDF

title = ''
startDate = ''
endDate = ''
today = ''
total_debit = 0
total_credit = 0

class PDF(FPDF):
    def header(self):
        self.set_font('Times', 'B', 20.0)
        self.set_xy(70, 10)
        self.cell(70, 10, title,
                  align='C')
        self.set_font('Times', '', 11.0)
        self.set_xy(70, 20)
        self.cell(70, 10, "From  {0}  To  {1}".format(startDate, endDate), align='C')
        self.set_xy(180, 10)
        self.cell(15, 10, 'Date', align='L')
        self.set_xy(180, 15)
        self.cell(15, 10, today, align='L')
        self.ln(15)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def table_body(self, header, data):
        self.set_font("Arial", size=12)  # Font style
        epw = self.w - 2 * self.l_margin  # Witdh of document
        col_width = self.w / 4.5  # Column width in table
        row_height = self.font_size * 1.5  # Row height in table

        self.add_page()

        spacing = 1.3  # Space in each cell

        self.ln(row_height * spacing)  # Define title line style

        col_width = [self.w / 20, self.w / 10, self.w / 1.75, self.w / 10, self.w / 10]

        # Add header
        for i, item in enumerate(header):
            self.set_font("Arial", 'B', size=12)  # for each column
            self.cell(col_width[i], row_height * spacing,  # Add a new cell
                     txt=str(item), border=1, align='L')
        self.ln(row_height * spacing)  # New line after header

        for row in data:
            self.set_font("Arial", size=8)  # For each row of the table
            for i, item in enumerate(row):  # For each cell in row
                self.cell(col_width[i], row_height * spacing,  # Add cell
                         txt=str(item), border=1)
            self.ln(row_height * spacing)  # Add line at the end of row

        # Add Footer
        footer = ["", "", "Total", str(total_debit), str(total_credit)]
        for i, item in enumerate(footer):
            self.set_font("Arial", 'B', size=8)  # for each column
            self.cell(col_width[i], row_height * spacing,  # Add a new cell
                      txt=str(item), border=1, align='L')
        self.ln(row_height * spacing)


    def print_table(self, header, data):
        self.table_body(header, data)


def create_trail_balance_pdf(_title, _startDate, _endDate, _today, _data, _buyers):

    global title
    global startDate
    global endDate
    global today

    global total_debit
    global total_credit

    total_debit = 0
    total_credit = 0

    title = _title
    startDate = _startDate
    endDate = _endDate
    today = _today

    header = ["Sr#", "Date", "Account Detail", "Debit", "Credit"]
    data = []

    for index, d in enumerate(_data):

        buyer = ''
        for b in _buyers:
            if d['Type'] == 'Day_Book':
                if str(b['_id']) == d['User_Id']:
                    buyer = b['Name'] + " (" + b['Address'] + ") - " + d['Remarks']
            else:
                if str(b['_id']) == d['User_Id']:
                    buyer = b['Name'] + " (" + b['Address'] + ")"

        if d['Pay_Type'] == 'Debit':
            data.append([str(index+1), d['Date_Time'], buyer, d['Amount'], 0])
            total_debit = total_debit + int(d['Amount'])
        else:
            data.append([str(index + 1), d['Date_Time'], buyer, 0, d['Amount']])
            total_credit = total_credit + int(d['Amount'])

    pdf = PDF()
    pdf.print_table(header, data)
    return pdf
    # pdf.output('tuto3.pdf', 'F')