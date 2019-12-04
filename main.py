"""
General structure

there will be an array of task objects(periodic and aperiodic)
this will be sent to a scheduling function which will return 
a class that includes the actual schedule, what missed, and 
other information

"""

"""
periodic task class
"""
class periodic_task:

	def __init__(self, comp_time, period):
		self.comp_time = comp_time
		self.period = period
		self.task_type = "periodic"

	def __repr__(self):
		return repr((self.task_type, self.comp_time, self.period))

	def get_comp_time(self):
		return self.comp_time

	def is_periodic(self):
		return True

	def get_period(self):
		return self.period

"""
aperiodic task class
"""
class aperiodic_task:

	def __init__(self, arrival_time, comp_time, deadline):
		self.arrival_time = arrival_time
		self.deadline = deadline
		self.comp_time = comp_time
		self.task_type = "aperiodic"

	def __repr__(self):
		return repr((self.task_type, self.arrival_time, self.comp_time, self.deadline))

	def get_comp_time(self):
		return self.comp_time

	def is_periodic(self):
		return False

"""
this class should serve as a holder for all scheduling results
including schedule, missed tasks, response times, etc.
"""
class schedule_report:

	def __init__(self, time):
		self.time = time
		self.schedule = [-1 for i in range(time)]

	def add_instance(self, time, task):
		self.schedule[time] = task

	def get_schedule(self):
		return self.schedule

	#this is a private method for building a string to represent the schedule
	def __get_task(self, time):
		if self.schedule[time] == -1:
			return "idle"
		else:
			return str(self.schedule[time])

	def __str__(self):
		ret_string = ""
		for i in range(self.time):
			ret_string += "t={0}, task_id={1}\n".format(i, self.__get_task(i))
		return ret_string



"""
the task id will be its index in the task array

each time slot we will need to
- run through and update each task

"""
def rms_scheduler(task_arr, time):

	#create a schedule report to return
	sr = schedule_report(time);

	print(len(task_arr))

	#change to true when task has finished for this instance
	has_executed = [False for i in range(len(task_arr))]
	time_left = [0 for i in range(len(task_arr))]

	#for loop to pick a task for each time slot
	for i in range(time):

		task_to_execute = None

		#search for lowest period task that hasnt ran yet
		for j in range(len(task_arr)):
			
			#update task information if it just arrived such as time left to execute and is finished
			if(task_arr[j].is_periodic() and (i == 0 or i % task_arr[j].get_period() == 0)):
				has_executed[j] = False
				time_left[j] = task_arr[j].get_comp_time()

			#if there is no task them the next periodic one that hasnt finished can execute
			if((task_to_execute == None) and (task_arr[j].is_periodic() == True) and (has_executed[j] == False)):
				task_to_execute = j
				continue #continue because this cant be lower then nothing

			#if this task has a lower period than current chosen one
			if(task_to_execute != None and task_arr[j].is_periodic() and has_executed[j] == False and 
				task_arr[j].get_period() < task_arr[task_to_execute].get_period()):
				task_to_execute = j

		if(task_to_execute != None):
			print("The current task for time " + str(i) + " is " + task_arr[task_to_execute].__repr__())
		else:
			print("idle for time " + str(i))

		if(task_to_execute == None):
			continue

		#need to subtract one time of execution in time_left and if 0 then finished also add to schedule report
		sr.add_instance(i, task_to_execute)

		time_left[task_to_execute] -= 1
		if time_left[task_to_execute] < 1:
			has_executed[task_to_execute] = True

	return sr

"""
the fair emergency first scheduling algorithm implementation
"""
def fair_emergency_scheduler(task_arr, time):


def main():
	
	task_list = []
	task_list.append(periodic_task(4, 6))
	task_list.append(aperiodic_task(1, 1, 2))
	# task_list.append(periodic_task(1, 3))
	# task_list.append(periodic_task(1, 4))

	sched_rep = rms_scheduler(task_list, 20)

	print(sched_rep)

if __name__ == "__main__":
	main()
