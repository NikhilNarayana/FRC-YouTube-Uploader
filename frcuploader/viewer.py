#!/usr/bin/env python3

from pyforms_lite import BaseWidget
from pyforms_lite.controls import ControlButton, ControlList


class OptionsViewer(BaseWidget):
	def __init__(self, pos, options):
		super(OptionsViewer, self).__init__(f"Queue #{pos}")
		self.options = options
		self.output = options.output
		self._oview = ControlList()
		self._oview.horizontal_headers = ["Key", "Value"]
		if pos:
			self._ignorebutton = ControlButton("Toggle Ignore")
			self._ignorebutton.value = self.__ignore_job
		self._oview.readonly = True
		for key, value in options.__dict__.items():
			if "output" not in key:
				self._oview += (key, value)
		self._oview.resize_rows_contents()
		if pos:
			self.formset = [{"Output": ["output"], "Values":["_oview"]}, "=", (" ", "_ignorebutton", " ")]
		else:
			self.formset = [{"Output": ["output"], "Values":["_oview"]}]

	def __ignore_job(self):
		self.options.ignore = False if self.options.ignore else True
		print(f"Ignore set to {self.options.ignore}")