import sys, os
import argparse
import subprocess

bulk_download_repo = "Discovery-BulkDownload"
utils_api_repo = "Discovery-UtilsAPI"
pytest_repo = "Discovery-PytestAutomation"

# Assumes you're in correct directory.
#		num_threads - pass None if not threadsafe
#		quit_of_first_fail - Bool
#		unknown_args - list, everything THIS argparse doesn't know about
def run_suite(num_threads, quit_on_first_fail, unknown_args):
	cmd = ["pytest", "-s"]
	if num_threads != None:
		cmd.extend(['-n', str(num_threads)])
	if quit_on_first_fail:
		cmd.extend(["-x"])
	cmd.extend(["."])
	cmd.extend(unknown_args)
	print("cmd:")
	print(" ".join(cmd))
	
	output = subprocess.run(cmd, shell=True)
	print(output.returncode)
if __name__ == "__main__":
	# Save your original dir, and switch to project root:
	original_dir = os.getcwd()
	project_root = os.path.dirname(os.path.abspath(__file__))
	os.chdir(project_root)

	# Custom argparse verify function(s):
	def check_thread_count(count):
		if count.lower() == 'auto':
			return 'auto'
		try:
			return int(count)
		except TypeError as e:
			raise argparse.ArgumentTypeError("Must pass an INT or 'auto' to '-n'. Error: {0}.".format(str(e)))

	# Setup argparse:
	parser = argparse.ArgumentParser(description='Runs each/all test cases for the SearchAPI project.')
	parser.add_argument('-x', action='store_true', 
		help="If used, quits as soon as a test fails.")
	parser.add_argument('-n', type=check_thread_count, nargs='?', default='auto',
		help="(INT/'auto') How many threads to use, for tests that support threading.")
	args, unknown_args = parser.parse_known_args()
	# Even with 'default', n can still be None if nothing was passed to it:
	if args.n == None:
		raise argparse.ArgumentTypeError("Must pass a value to '-n'.")

	# Run UtilsAPI suite:
	os.chdir(os.path.join(project_root,utils_api_repo,pytest_repo))
	run_suite(args.n, args.x, unknown_args)
	# Switch back to whatever dir you were in:
	os.chdir(original_dir)