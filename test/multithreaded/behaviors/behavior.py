
class Behavior:
	def execute(self, previousBehavior):
		"""Executes the code for this behavior (should take very little time). Returns the pilot commands"""
		raise NotImplementedError()

	def getPriority(self):
		return 0

