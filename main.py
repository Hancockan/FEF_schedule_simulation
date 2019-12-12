"""
General structure

there will be an array of task objects(periodic and aperiodic)
this will be sent to a scheduling function which will return 
a class that includes the actual schedule, what missed, and 
other information

"""

import uuid


class aperiodic_server:

	def __init__(self, comp_time, period):
		self.comp_time = comp_time
		self.period = period

"""
periodic task class
"""
class periodic_task:

	def __init__(self, comp_time, period, deadline_type):
		self.comp_time = comp_time
		self.period = period
		self.task_type = "periodic"
		self.deadline_type = deadline_type

	def __repr__(self):
		return repr((self.task_type, self.comp_time, self.period))

	def get_comp_time(self):
		return self.comp_time

	def is_periodic(self):
		return True

	def get_period(self):
		return self.period

	def get_deadline_type(self):
		return self.deadline_type

"""
aperiodic task class
"""
class aperiodic_task:

	def __init__(self, arrival_time, comp_time, deadline, deadline_type):
		self.arrival_time = arrival_time
		self.deadline = deadline
		self.comp_time = comp_time
		self.task_type = "aperiodic"
		self.deadline_type = deadline_type #hard or soft

	def __repr__(self):
		return repr((self.task_type, self.arrival_time, self.comp_time, self.deadline))

	def get_comp_time(self):
		return self.comp_time

	def is_periodic(self):
		return False

	def get_deadline_type(self):
		return self.deadline_type

	def get_deadline(self):
		return self.deadline

	def get_arr_time(self):
		return self.arrival_time

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

task with lowest period is executed

TODO
- add in aperiodic server

- currently doesn't matter whether task is hard or soft
"""
def rms_scheduler(task_arr, time):

	#create a schedule report to return
	sr = schedule_report(time);

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

		# if(task_to_execute != None):
		# 	print("The current task for time " + str(i) + " is " + task_arr[task_to_execute].__repr__())
		# else:
		# 	print("idle for time " + str(i))

		if(task_to_execute == None):
			continue

		#need to subtract one time of execution in time_left and if 0 then finished also add to schedule report
		sr.add_instance(i, task_to_execute)

		time_left[task_to_execute] -= 1
		if time_left[task_to_execute] < 1:
			has_executed[task_to_execute] = True

	return sr


#check if there exists periodic tasks that haven't executed
def get_periodic_task(task_arr, has_executed):
	for i in range(len(task_arr)):
		tsklist = []
		if(task_arr[i].is_periodic() and has_executed[i] == False):
			tsklist.append(task_arr[i])
		return tsklist

#check if soft aperiodic tasks exist
def get_aperiodic_soft(task_arr, has_executed, time):
	tsklist = []
	for i in range(len(task_arr)):
		if(task_arr[i].is_periodic() == False and has_executed[i] == False and task_arr[i].get_arr_time() >= time):
			tsklist.append(task_arr[i])
	return tsklist

"""
the fair emergency first scheduling algorithm implementation
"""
def fair_emergency_scheduler(task_arr, time):
	
	sr = schedule_report(time)
	has_executed = [False for i in range(len(task_arr))]
	time_left = [0 for i in range(len(task_arr))]

	for i in range(time):

		task_to_execute = None
		hard_aprd_tsks = []

		##########

		#need to reset all task stats 
		for j in range(len(task_arr)):
			
			#update task information if it just arrived such as time left to execute and is finished
			if(task_arr[j].is_periodic() and (i == 0 or i % task_arr[j].get_period() == 0)):
				has_executed[j] = False
				time_left[j] = task_arr[j].get_comp_time()

		##########

		#if there exists an aperiodic task with a hard deadline run the one with the earliest deadline
		for j in range(len(task_arr)):
			if(task_arr[j].is_periodic() == False and task_arr[j].get_deadline_type() == "hard" 
				and task_arr[j].get_arr_time() <= i):
				hard_aprd_tsks.append(task_arr[j])

		#look through list of hard aperiodic tasks for one with closest deadline
		if(len(hard_aprd_tsks) > 0):
			task_to_execute = hard_aprd_tsks[0]
			for j in range(len(hard_aprd_tsks)):
				if hard_aprd_tsks[j].get_deadline() < hard_aprd_tsks[task_to_execute].get_deadline():
					task_to_execute = j
			continue 

		##########

		#get list of periodic and soft aperiodic tasks
		period_tasks = get_periodic_task(task_arr, has_executed)
		soft_aprd = get_aperiodic_soft(task_arr, has_executed, i)

		if(len(soft_aprd) > 0 and len(period_tasks) == 0):
			task_to_execute = soft_aprd[0]
			#run soft apeiodic task with closest deadline
			for w in range(len(soft_aprd)):
				if(soft_aprd[w].get_deadline() < soft_aprd[task_to_execute].get_deadline()):
					task_to_execute = w

		#####Need to fix all above that use a task index to rather use a task id generated when it is intstantiated



def main():
	
	task_list = []
	task_list.append(periodic_task(4, 6, "hard"))
	task_list.append(aperiodic_task(1, 1, 2, "soft"))
	# task_list.append(periodic_task(1, 3))
	# task_list.append(periodic_task(1, 4))

	sched_rep = rms_scheduler(task_list, 20)

	print(sched_rep)

	print(uuid.uuid1())

if __name__ == "__main__":
	main()
