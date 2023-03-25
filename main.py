import pandas as pd
import wx
import wx.grid
import os
import matplotlib.pyplot as plt
import numpy as np


# Filters Dialog
class FiltersDialog (wx.Dialog):
	def __init__(self, user_input):
		super().__init__(parent=None, id=wx.ID_ANY, title="Filter Options", size=wx.DefaultSize)
		self.sizer = wx.FlexGridSizer(7, 1, 0, 0)
		self.sizer.AddGrowableRow(6)  # Makes last row expandable so that the 'Apply Filters' button centers itself
		self.sizer.AddGrowableCol(0) # There is only one column, and it will take up the width of the window.
		self.sizer.SetFlexibleDirection(wx.BOTH)

		# Separate sizer to position date filter text fields
		self.date_sizer = wx.BoxSizer(wx.HORIZONTAL)

		# Filter by Date
		self.date_label = wx.StaticText(self, label="Filter by Date:")
		self.date_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		self.sizer.Add(self.date_label, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

		self.from_label = wx.StaticText(self, label="From:")
		self.date_sizer.Add(self.from_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		# --------------------------------------------------------------------------------------------------------------
		# Pre-fill fields with prior user input, if exists
		if user_input['from']:
			self.from_field = wx.TextCtrl(self, value=user_input['from'])
		else:
			self.from_field = wx.TextCtrl(self)
		# --------------------------------------------------------------------------------------------------------------
		self.date_sizer.Add(self.from_field, 0, wx.ALIGN_CENTER_VERTICAL, 5)

		self.to_label = wx.StaticText(self, label="To:")
		self.date_sizer.Add(self.to_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		# --------------------------------------------------------------------------------------------------------------
		# Pre-fill fields with prior user input, if exists
		if user_input['to']:
			self.to_field = wx.TextCtrl(self, value=user_input['to'])
		else:
			self.to_field = wx.TextCtrl(self)
		# --------------------------------------------------------------------------------------------------------------
		self.date_sizer.Add(self.to_field, 0, wx.ALIGN_CENTER_VERTICAL, 5)

		self.sizer.Add(self.date_sizer, 1, wx.ALIGN_CENTER, 5)

		# Horizontal Line
		self.line_one = wx.StaticLine(self, wx.LI_HORIZONTAL)
		self.sizer.Add(self.line_one, 0, wx.EXPAND | wx.ALL, 5)

		# Filter by Accident Type
		self.accident_type_label = wx.StaticText(self, label="Filter by Accident Type:")
		self.accident_type_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		self.sizer.Add(self.accident_type_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
		# --------------------------------------------------------------------------------------------------------------
		# Pre-fill fields with prior user input, if exists
		if user_input['accident_type']:
			self.accident_type_field = wx.TextCtrl(self, value=user_input['accident_type'])
		else:
			self.accident_type_field = wx.TextCtrl(self)
		self.sizer.Add(self.accident_type_field, 0, wx.ALIGN_CENTER | wx.ALL, 5)
		# --------------------------------------------------------------------------------------------------------------
		# Horizontal Line
		self.line_one = wx.StaticLine(self, wx.LI_HORIZONTAL)
		self.sizer.Add(self.line_one, 0, wx.EXPAND | wx.ALL, 5)

		# Separate sizer for 'apply' and 'reset' buttons to be side-by-side
		self.btn_pair_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.btn_pair_sizer, 0, wx.ALIGN_CENTER)

		# Filter Button
		self.filter_btn = wx.Button(self, label="APPLY FILTERS")
		self.filter_btn.SetMinSize(wx.Size(150, -1))
		self.btn_pair_sizer.Add(self.filter_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
		self.filter_btn.Bind(wx.EVT_BUTTON, self.apply_filters)

		# Reset Button
		self.reset_btn = wx.Button(self, label="RESET")
		self.reset_btn.SetMinSize(wx.Size(150, -1))
		self.btn_pair_sizer.Add(self.reset_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
		self.reset_btn.Bind(wx.EVT_BUTTON, self.reset_filters)

		# Positioning
		self.SetSizer(self.sizer)
		self.Layout()
		self.Centre(wx.BOTH)

		self.Bind(wx.EVT_CLOSE, self.on_close)

	# Resets table to represent original imported data
	def reset_filters(self, event):
		# Set the user input that was stored to empty strings
		self.accident_type_field.Value = ""
		self.to_field.Value = ""
		self.from_field.Value = ""

		if window.panel_two.user_input['from'] != "" or window.panel_two.user_input['to'] != "" or window.panel_two.user_input['accident_type'] != "":
			window.panel_two.reset_grid()
			window.panel_two.filter_table(date={"from": None, "to": None}, accident_type=None)

			window.panel_two.user_input = {
				'from': "",
				'to': "",
				'accident_type': ""
			}

	# Clears grid and passes user input for filtering
	def apply_filters(self, event):
		if self.from_field.GetValue() != window.panel_two.user_input['from'] or self.to_field.GetValue() != window.panel_two.user_input['to'] or self.accident_type_field.GetValue() != window.panel_two.user_input['accident_type']:
			# Clear the grid in preparation for rebuilding with new rows
			window.panel_two.reset_grid()

			# Calling the filter function with the user input as parameters
			window.panel_two.filter_table(
				date={"from": self.from_field.GetValue(), "to": self.to_field.GetValue()},
				accident_type=self.accident_type_field.GetValue()
			)

	# Updates the instance variable for the modal window in the panel_two object, which helps in ensuring only one
	# filter dialog is instantiated at any one time.
	def on_close(self, event):
		window.panel_two.modal = None

		self.Destroy()


# Loading Bar Dialog
class LoadingDialog (wx.Dialog):
	def __init__(self):
		super().__init__(parent=None, id=wx.ID_ANY, title=wx.EmptyString, size=wx.DefaultSize, style=0)

		self.sizer = wx.BoxSizer(wx.VERTICAL)

		# Loading Gauge dimensions/positioning
		self.l_gauge = wx.Gauge(self, wx.ID_ANY, 0, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
		self.l_gauge.SetValue(0)
		self.sizer.Add(self.l_gauge, 0, wx.ALL, 5)
		self.SetSizer(self.sizer)
		self.Layout()
		self.sizer.Fit(self)
		self.Show()
		self.Centre(wx.BOTH)


# File Selection Screen
class PanelOne (wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.currentDirectory = os.getcwd()
		self.parent = parent
		self.panel = wx.Panel(self)

		# Header (program name)
		self.header = wx.StaticText(self, label="Road Crash Data Analyzer")
		self.header.SetFont(wx.Font(50, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		self.sizer.Add(self.header, 0, wx.ALIGN_CENTER | wx.TOP, 60)

		# Subtitle (version number)
		self.subtitle = wx.StaticText(self, label="Version 1.0")
		self.subtitle.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
		self.sizer.Add(self.subtitle, 0, wx.ALIGN_CENTER | wx.TOP, 15)

		# File Prompt Text
		self.file_prompt = wx.StaticText(self, label="Select datasheet to analyze:")
		self.file_prompt.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.sizer.Add(self.file_prompt, 0, wx.ALIGN_CENTER | wx.TOP, 500)

		# Browse File Button
		self.file_button = wx.Button(self, label="BROWSE FILE")
		self.file_button.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.file_button.SetMinSize(wx.Size(175, -1))
		self.sizer.Add(self.file_button, 0, wx.ALIGN_CENTER | wx.TOP, 10)
		self.file_button.Bind(wx.EVT_BUTTON, self.on_open_file)

		self.SetSizer(self.sizer)

	# Opens file dialog, specifies valid file types, and reads selected file.
	def on_open_file(self, event):
		dlg = wx.FileDialog(
			self, message="Choose a file",
			defaultDir=self.currentDirectory,
			defaultFile="",
			wildcard="Microsoft Excel Comma Separated Values File (*.csv)|*.csv",
			style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_CANCEL:
			return
		pathname = dlg.GetPath()
		try:
			with open(pathname, 'r') as file:
				df = pd.read_csv(file)
				self.parent.panel_two.set_file_name(os.path.basename(pathname))
				self.parent.panel_two.set_up_table(df)
				self.parent.panel_two.df_original = df
		except IOError:
			wx.LogError("Cannot open file")
		dlg.Destroy()
		self.parent.swap(2)


# Main Data Table Screen
class PanelTwo (wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parent = parent

		self.modal = None  # Initialization of modal window
		self.file_name = ""  # Initialization of file name
		self.df_original = ""  # Initialization of dataframe for storing original data
		self.df_table = ""  # Initialization of dataframe for storing filtered data
		self.user_input = {'from': "", 'to': "", 'accident_type': ""}

		# File Name
		self.file_header = wx.StaticText(self, label=self.file_name)
		self.file_header.SetFont(wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		self.sizer.Add(self.file_header, 0, wx.ALIGN_LEFT | wx.ALL, 35)

		# Filter Button
		self.filter_btn = wx.Button(self, label="Filter")
		self.filter_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.filter_btn.SetMinSize(wx.Size(100, -1))
		self.filter_btn.Bind(wx.EVT_BUTTON, self.open_filters)
		self.sizer.Add(self.filter_btn, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 20)

		# Data Grid
		self.grid = wx.grid.Grid(self)
		self.grid.CreateGrid(0, 0)
		self.grid.EnableEditing(False)
		self.grid.SetMaxSize(wx.Size(-1, 800))
		self.sizer.Add(self.grid, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 21)

		# Chart Button
		chart_choices = ["Generate Chart", "Region Distribution", "Accidents by Hour", "Alcohol Analysis"]
		self.chart_btn = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, chart_choices, 0)
		self.chart_btn.SetSelection(0)
		self.chart_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.sizer.Add(self.chart_btn, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, 20)
		self.chart_btn.Bind(wx.EVT_CHOICE, self.chart_gen)
		self.SetSizer(self.sizer)

	# Clears grid (removes the values in all cells) and deletes every single row (if there are any).
	def reset_grid(self):
		self.grid.ClearGrid()
		if self.grid.NumberRows > 0:
			self.grid.DeleteRows(pos=0, numRows=self.grid.GetNumberRows())

	# Performs the filter operations on the dataframe (selecting the proper rows according to the
	# options selected by user)
	def filter_table(self, date, accident_type):
		df = self.df_original  # Use the untouched original dataframe

		# Storing the filters in the panel_two object
		window.panel_two.user_input = {
			'from': date['from'],
			'to': date['to'],
			'accident_type': accident_type
		}

		# If the date object contains values for 'from' or 'to', then we take steps to filter the table by date.
		if date['from'] or date['to']:

			# The dates provided by the user, as well as all the dates in the dataframe, are converted to datetime
			# objects (so they can be used to select the proper rows).
			date['from'] = pd.to_datetime(date['from'], dayfirst=True)
			date['to'] = pd.to_datetime(date['to'], dayfirst=True)
			df['ACCIDENT_DATE'] = pd.to_datetime(df['ACCIDENT_DATE'], dayfirst=True)

			# First we check if there is value in both 'from' and 'to', since that will require a specific range of
			# rows to be selected.
			if pd.isnull(date['from']) is False and pd.isnull(date['to']) is False:
				df = df.loc[df['ACCIDENT_DATE'].isin(pd.date_range(date['from'], date['to']))]

			# If only 'from' has a value, then we select all rows with later dates.
			elif pd.isnull(date['from']) is False:
				df = df.loc[df['ACCIDENT_DATE'] > date['from']]

			# Likewise, if only 'to' has a value, then we select all rows with earlier dates.
			elif pd.isnull(date['to']) is False:
				df = df.loc[df['ACCIDENT_DATE'] < date['to']]

			# The dataframe is sorted by the ACCIDENT_DATE, since it's relevant if the user specified a date filter.
			df = df.sort_values(by=['ACCIDENT_DATE'], ascending=True, kind='stable')

			# The values in the ACCIDENT_DATE column are formatted in the original style for consistency.
			df['ACCIDENT_DATE'] = df['ACCIDENT_DATE'].dt.strftime('%d/%m/%Y')

		# If the user specified an accident type, then we simply select all rows that have a value for ACCIDENT_TYPE
		# that includes the keywords given by the user (case-insensitive)
		if accident_type:
			df = df.loc[df['ACCIDENT_TYPE'].str.contains(accident_type, case=False)]

		# The table is rebuilt
		self.rebuild_table(df)

	# Rebuilds table for filtered dataframe
	def rebuild_table(self, df):
		self.df_table = df  # The filtered dataframe is assigned to the instance variable in panel_two

		# Instantiate and show the loading dialog
		dlg = LoadingDialog()
		dlg.Show()

		# Insert rows according to the shape of the dataframe (columns still persist and don't need to be added again)
		self.grid.InsertRows(0, df.shape[0])

		# The loading gauge is set according to the number of rows
		dlg.l_gauge.SetRange(self.grid.GetNumberRows())

		# Gauge value is initialized
		v = 0

		# Index for counting rows is initialized
		row_count = 0

		# itertuples is used to create tuples for each row and the entire dataframe is looped through
		for i in df.itertuples():
			for j in range(self.grid.GetNumberCols()):
				self.grid.SetCellValue(row_count, j, str(i[j + 1]))
			row_count += 1
			v += 1
			dlg.l_gauge.SetValue(v)  # Loading gauge is updated to reflect the progress of the loop

		# Destroy loading dialog when done
		dlg.Destroy()

	# Stores file name of the file selected by user
	def set_file_name(self, name):
		self.file_header.SetLabel(name)

	# Handles which chart is generated according to combo box selection
	def chart_gen(self, event):
		if self.chart_btn.GetSelection() == 1:
			self.generate_regions()
		elif self.chart_btn.GetSelection() == 2:
			self.generate_hourly_accidents()
		elif self.chart_btn.GetSelection() == 3:
			self.generate_alcohol_analysis()
		self.chart_btn.SetSelection(0)

	# Generates chart for distribution of accidents by region
	def generate_regions(self):
		region_accidents = self.df_table['REGION_NAME'].value_counts()
		plt.figure(figsize=(10, 7))

		# autopct parameter handles the formatting of the labels for each slice of the pie, using a lambda function
		# here to calculate the percentages to display
		region_accidents.plot.pie(autopct=lambda p: '{:.2f}%({:0f})'.format(p, (p/100)*region_accidents.sum()))

		# Bunch of if statements to create a chart title based on the filter options selected by user, thereby
		# making the chart more readable and accurate
		if self.user_input['from'] and self.user_input['to']:
			title = f'Distribution of Accidents by Region between {self.user_input["from"]} and {self.user_input["to"]}'
		elif self.user_input['from']:
			title = f'Distribution of Accidents by Region from {self.user_input["from"]} onwards'
		elif self.user_input['to']:
			title = f'Distribution of Accidents by Region up to {self.user_input["to"]}'
		else:
			title = "Distribution of Accidents by Region"

		if self.user_input['accident_type']:
			title += f", \n filtered for '{self.user_input['accident_type']}' accidents"

		plt.title(title)
		plt.ylabel('')

		plt.show()

	# Generates chart for number of accidents by hour.
	def generate_hourly_accidents(self):
		hourly_accidents = self.df_table
		df2 = pd.to_datetime(hourly_accidents['ACCIDENT_TIME'], format="%H.%M.%S").dt.hour

		graph = df2.groupby(df2).size()
		plt.figure(figsize=(10,5))
		graph.plot.bar('Time', 'Accidents', color=['tomato'])

		# Bunch of if statements to create a chart title based on the filter options selected by user, thereby
		# making the chart more readable and accurate
		if self.user_input['from'] and self.user_input['to']:
			title = f'Number of Accidents per Hour between {self.user_input["from"]} and {self.user_input["to"]}'
		elif self.user_input['from']:
			title = f'Number of Accidents per Hour from {self.user_input["from"]} onwards'
		elif self.user_input['to']:
			title = f'Number of Accidents per Hour up to {self.user_input["to"]}'
		else:
			title = "Number of Accidents per Hour"

		if self.user_input['accident_type']:
			title += f", \n filtered for '{self.user_input['accident_type']}' accidents"

		plt.title(title)

		plt.xlabel('Time of Day (24hr)')
		plt.ylabel('Number of Accidents')
		plt.show()

	# Generates grouped bar chart for alcohol analysis
	def generate_alcohol_analysis(self):
		# The dataframe is split into two here, separating the records where alcohol was not present from the records
		# where it was. This allows us to analyse the two separately and create a grouped bar chart.
		non_alcohol_accidents = self.df_table.loc[self.df_table['ALCOHOLTIME'] == "No"]
		alcohol_accidents = self.df_table.loc[self.df_table['ALCOHOLTIME'] == "Yes"]

		# The two dataframes have a value count performed, yielding separate series for the frequency of accident
		# types for those that involved alcohol and for thoes that didn't
		bar1 = non_alcohol_accidents['ACCIDENT_TYPE'].value_counts()
		bar2 = alcohol_accidents['ACCIDENT_TYPE'].value_counts()

		# Initialization of arrays that will store only the values from the series above
		y1 = []
		y2 = []

		# Stores all the accident types found in the dataframe, used to label the y-ticks in the graph
		labels = []

		# We loop through one of the series to retrieve the accident types and store them in the labels array
		for val, cnt in bar1.items():
			labels.append(val)

		# We loop through the label arrays and use the elements in it as a key so we pull out the values from the
		# two series
		for accident_type in labels:
			y1.append(bar1[accident_type])
			y2.append(bar2[accident_type])

		# We use the length of one of the arrays to determine how many y-ticks there should be in the graph
		x = np.arange(len(y1))

		# --------------------------------------------------------------------------------------------------------------
		# PLOTTING
		plt.figure(figsize=(12, 6))
		plt.barh(x - .2, y1, height=.4)
		plt.barh(x + .2, y2, height=.4)
		plt.xlabel("Number of Accidents")
		plt.yticks(x, labels, fontsize=9, ha='right')
		plt.ylabel("Accident Type")

		# If statements to generate relevant title
		if self.user_input['from'] and self.user_input['to']:
			title = f"Breakdown of Accidents by Type and Alcohol Presence between {self.user_input['from']} and {self.user_input['to']}"
		elif self.user_input['from']:
			title = f"Breakdown of Accidents by Type and Alcohol Presence from {self.user_input['from']} onwards"
		elif self.user_input['to']:
			title = f"Breakdown of Accidents by Type and Alcohol Presence up to {self.user_input['to']}"
		else:
			title = "Breakdown of Accidents by Type and Alcohol Presence"

		plt.title(title)
		plt.legend(['Alcohol Not Present', 'Alcohol Present'])
		plt.tight_layout()
		# --------------------------------------------------------------------------------------------------------------

		plt.show()

	# Handles the transferal of data from the .csv file to the grid.
	def set_up_table(self, df):
		# Dataframe is first stored in an instance variable of the PanelTwo class.
		self.df_table = df
		# Displays non-modal dialog (LoadingDialog class)
		dlg = LoadingDialog()
		dlg.Show()

		# Insert rows and columns according to shape (number of rows and columns) of dataframe
		self.grid.InsertRows(0, df.shape[0])
		self.grid.InsertCols(0, df.shape[1])

		# Set the range (maximum value) of loading gauge according to number of columns
		dlg.l_gauge.SetRange(self.grid.GetNumberRows())

		# Initialize index
		i = 0

		# Loop through columns in dataframe and add their labels to the grid columns
		for col in df.columns:
			self.grid.SetColLabelValue(i, col)
			i += 1

		# Initialize gauge value
		v = 0

		row_count = 0  # Use this to provide a row index

		# Each row in the dataframe is transformed into a tuple and then iterated through. This allows for far more
		# efficient looping; all the information in the row, with column names, is stored in one memory location at a
		# time (the index, or i).
		for i in self.df_table.itertuples():
			for j in range(self.grid.GetNumberCols()):
				self.grid.SetCellValue(row_count, j, str(i[j + 1]))

			row_count += 1
			# Each time a loop over a row is complete, the gauge value is increased by one.
			v += 1
			dlg.l_gauge.SetValue(v)

		# Automatically resize column widths now that they are populated
		self.grid.AutoSizeColumns()

		# Loading bar dialog is deleted
		dlg.Destroy()

	def open_filters(self, event):
		if self.modal is None:
			self.modal = FiltersDialog(user_input=self.user_input)
			self.modal.Show()


# Main Window
class Window (wx.Frame):

	def __init__(self, title):
		super().__init__(parent=None, title=title, size=wx.Size(1920, 1080))

		# Instantiate the panels (screens)
		self.panel_one = PanelOne(self)
		self.panel_two = PanelTwo(self)
		self.panel_two.Hide()

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.panel_one, 1, wx.EXPAND)
		self.sizer.Add(self.panel_two, 1, wx.EXPAND)
		self.SetSizer(self.sizer)
		self.Show()
		self.Centre(wx.BOTH)

	# Switches which panel is currently visible
	def swap(self, num):
		if num == 1:
			self.panel_one.Show()
			self.panel_two.Hide()
		if num == 2:
			self.panel_two.Show()
			self.panel_one.Hide()
		self.Layout()

	# Stores name of the file selected by user in panel_two object.
	def set_file_name(self, name):
		self.panel_two.file_name = name


app = wx.App()
window = Window("Road Crash Data Analyzer")
window.Show()
app.MainLoop()
