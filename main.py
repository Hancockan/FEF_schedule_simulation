"""
General structure

there will be an array of task objects(periodic and aperiodic)
this will be sent to a scheduling function which will return 
a class that includes the actual schedule, what missed, and 
other information

"""

import uuid
import random


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
		self.id = uuid.uuid1()

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

	def get_id(self):
		return self.id

	def __str__(self):
		return "({0}, {1}) {2}".format(self.comp_time, self.period, self.deadline_type)

	def get_deadline(self, time):
		i = time
		while True:
			i += 1
			if i % self.get_period() == 0:
				return i

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
		self.id = uuid.uuid1()

	def __repr__(self):
		return "aperiodic_task({0}, {1}, {2}, {3})".format(self.arrival_time, 
			self.comp_time, self.deadline, self.deadline_type)

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

	def get_id(self):
		return self.id

	def __str__(self):
		return "arr: {0} cpt: {1} ddl: {2} type: {3}".format(self.arrival_time, self.comp_time, 
			self.deadline, self.deadline_type)

"""
this class should serve as a holder for all scheduling results
including schedule, missed tasks, response times, etc.
"""
class schedule_report:

	def __init__(self, time, task_arr, aprd_svr):
		self.tsk_server = aprd_svr
		self.tasks = task_arr
		self.time = time
		self.schedule = [-1 for i in range(time)]
		self.missed_task_instances = [0 for i in range(len(task_arr))]
		self.miss_dict = {'hard_prd': 0, 'soft_prd': 0, 'hard_aprd': 0, 'soft_aprd': 0}

	#perform analysis at the end
	def finalize(self):
		print('this function currently doesnt do anything')
		#count all misses into the dicitonary

	#periodic tasks
	def missed_instance(self, task):
		for i in range(len(self.tasks)):
			if self.tasks[i].get_id() == task.get_id():
				self.missed_task_instances[i] += 1

				#count to the misses dictionary unless this is the task server
				if i == len(self.tasks) - 1 and self.tsk_server: # FEF wont have a periodic task at the end
					break
				if self.tasks[i].get_deadline_type() == "hard":
					self.miss_dict['hard_prd'] += 1
				else:
					self.miss_dict['soft_prd'] += 1
				break # to not aimlessly search through other ids

	def count_aperiodic_misses(self, time_left):
		for i in range(len(time_left)):
			#if the task is aperiodic and there is time left
			if self.tasks[i].is_periodic() == False and time_left[i] > 0:
				if self.tasks[i].get_deadline_type() == "hard":
					self.miss_dict['hard_aprd'] += 1
				else:
					self.miss_dict['soft_aprd'] += 1
			#don't want to count any time left on periodic tasks

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
		# ret_string += str(self.missed_task_instances)
		ret_string += str(self.miss_dict)
		return ret_string

#check if soft aperiodic tasks exist
def get_aperiodic_soft(task_arr, has_executed, time):
	tsklist = []
	for i in range(len(task_arr)):
		if(task_arr[i].is_periodic() == False and has_executed[i] == False and task_arr[i].get_arr_time() <= time
			and task_arr[i].get_deadline_type() == "soft"):
			tsklist.append(task_arr[i])
	return tsklist

#check if hard aperiodic tasks exist
def get_aperiodic_hard(task_arr, has_executed, time):
	tsklist = []
	for i in range(len(task_arr)):
		if(task_arr[i].is_periodic() == False and has_executed[i] == False and task_arr[i].get_arr_time() <= time
			and task_arr[i].get_deadline_type() == "hard" and task_arr[i].get_deadline() > time):
			tsklist.append(task_arr[i])
	return tsklist

def deduct_unit_of_execution(task, task_arr, has_executed, time_left):
	for i in range(len(task_arr)):
		if task.get_id() == task_arr[i].get_id():
			time_left[i] = time_left[i] - 1
			if time_left[i] < 1:
				has_executed[i] = True
			return

# def get_aperiodic_tsk_server(task_arr, time):


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

	#add a task for an aperiodic task server - giving it 30% possible utilization
	tsk_server = periodic_task(3, 10, "hard") # no current use of deadline type
	tsk_server_id = tsk_server.get_id()
	task_arr.append(tsk_server)

	#create a schedule report to return
	sr = schedule_report(time, task_arr, True);

	#change to true when task has finished for this instance
	has_executed = [False for i in range(len(task_arr))]
	time_left = [0 for i in range(len(task_arr))]

	#for loop to pick a task for each time slot
	for i in range(time):

		task_to_execute = None
		tsk_server_slot = False

		#search for lowest period task that hasnt ran yet
		for j in range(len(task_arr)):
			
			#update task information if it just arrived such as time left to execute and is finished
			if(task_arr[j].is_periodic() and (i == 0 or i % task_arr[j].get_period() == 0)):
				if time_left[j] != 0:
					sr.missed_instance(task_arr[j])
				has_executed[j] = False
				time_left[j] = task_arr[j].get_comp_time()

			if(task_arr[j].is_periodic() == False and task_arr[j].get_arr_time() == i):
				time_left[j] = task_arr[j].get_comp_time()

			#if there is no task them the next periodic one that hasnt finished can execute
			if((task_to_execute == None) and (task_arr[j].is_periodic() == True) and (has_executed[j] == False)):
				task_to_execute = task_arr[j]
				continue #continue because this cant be lower then nothing

			#if this task has a lower period than current chosen one
			if(task_to_execute != None and task_arr[j].is_periodic() and has_executed[j] == False and 
				task_arr[j].get_period() < task_to_execute.get_period()):
				task_to_execute = task_arr[j]

		# if this is the aperiodic task server
		if task_to_execute != None and task_to_execute.get_id() == tsk_server_id:
			tsk_server_slot = True

			# get an aperiodic task to execute - hard deadlines first
			hard_aprd_tsks = get_aperiodic_hard(task_arr, has_executed, i)
			soft_aprd_tsks = get_aperiodic_soft(task_arr, has_executed, i)

			if len(hard_aprd_tsks) > 0:
				task_to_execute = hard_aprd_tsks[0]
				for j in range(len(hard_aprd_tsks)):
					if hard_aprd_tsks[j].get_deadline() < task_to_execute.get_deadline():
						task_to_execute = hard_aprd_tsks[j]
			elif len(soft_aprd_tsks) > 0:
				task_to_execute = soft_aprd_tsks[0]
				for j in range(len(soft_aprd_tsks)):
					if soft_aprd_tsks[j].get_deadline() < task_to_execute.get_deadline():
						task_to_execute = soft_aprd_tsks[j]

			# if the there was no aperiodic task to assign to the server, go idle
			if task_to_execute.get_id() == tsk_server_id:
				task_to_execute = None

		#need to subtract one time of execution in time_left and if 0 then finished also add to schedule report
		sr.add_instance(i, task_to_execute)

		if(task_to_execute == None):
			continue

		#For the aperiodic server this will take care of the aperiodic task
		deduct_unit_of_execution(task_to_execute, task_arr, has_executed, time_left)

		if tsk_server_slot:
			time_left[len(time_left) - 1] -=1
			if time_left[len(time_left) - 1] < 1:
				has_executed[len(has_executed) - 1] = True

	sr.count_aperiodic_misses(time_left)

	# sr.finalize()
	return sr


#check if there exists periodic tasks that haven't executed
def get_periodic_task(task_arr, has_executed):
	tsklist = []
	for i in range(len(task_arr)):
		if(task_arr[i].is_periodic() and has_executed[i] == False):
			tsklist.append(task_arr[i])
	return tsklist

#check if hard periodic task exists
def get_hard_periodic_tsks(task_arr, has_executed):
	tsk_list = []
	for i in range(len(task_arr)):
		if task_arr[i].is_periodic() and task_arr[i].get_deadline_type() == "hard" and has_executed[i] == False:
			tsk_list.append(task_arr[i])
	return tsk_list

#check if soft periodic task exists
def get_soft_periodic_tsks(task_arr, has_executed):
	tsk_list = []
	for i in range(len(task_arr)):
		if task_arr[i].is_periodic() and task_arr[i].get_deadline_type() == "soft" and has_executed[i] == False:
			tsk_list.append(task_arr[i])
	return tsk_list

"""
the fair emergency first scheduling algorithm implementation
"""
def fair_emergency_scheduler(task_arr, time):
	
	sr = schedule_report(time, task_arr, False)
	has_executed = [False for i in range(len(task_arr))]
	time_left = [0 for i in range(len(task_arr))]

	for i in range(time):

		task_to_execute = None
		hard_aprd_tsks = []

		#need to reset all task stats 
		for j in range(len(task_arr)):
			
			#update task information if it just arrived such as time left to execute and is finished
			if(task_arr[j].is_periodic() and (i == 0 or i % task_arr[j].get_period() == 0)):
				if time_left[j] != 0:
					sr.missed_instance(task_arr[j])
				has_executed[j] = False # must be reset each time it arrives
				time_left[j] = task_arr[j].get_comp_time()

			if(task_arr[j].is_periodic() == False and task_arr[j].get_arr_time() == i):
				time_left[j] = task_arr[j].get_comp_time()

		#if there exists an aperiodic task with a hard deadline run the one with the earliest deadline
		for j in range(len(task_arr)):
			if(task_arr[j].is_periodic() == False and task_arr[j].get_deadline_type() == "hard" 
				and task_arr[j].get_arr_time() <= i and has_executed[j] == False):
				hard_aprd_tsks.append(task_arr[j])

		#look through list of hard aperiodic tasks for one with closest deadline
		if(len(hard_aprd_tsks) > 0):
			task_to_execute = hard_aprd_tsks[0]
			for j in range(len(hard_aprd_tsks)):
				if hard_aprd_tsks[j].get_deadline() < task_to_execute.get_deadline():
					task_to_execute = hard_aprd_tsks[j]
			sr.add_instance(i, task_to_execute)
			deduct_unit_of_execution(task_to_execute, task_arr, has_executed, time_left)
			continue 

		#get list of periodic and soft aperiodic tasks
		period_tasks = get_periodic_task(task_arr, has_executed)
		soft_aprd = get_aperiodic_soft(task_arr, has_executed, i)

		if(len(soft_aprd) > 0 and len(period_tasks) == 0):
			task_to_execute = soft_aprd[0]
			#run soft apeiodic task with closest deadline
			for w in range(len(soft_aprd)):
				if(soft_aprd[w].get_deadline() < task_to_execute.get_deadline()):
					task_to_execute = soft_aprd[w]
			sr.add_instance(i, task_to_execute)
			deduct_unit_of_execution(task_to_execute, task_arr, has_executed, time_left)
			continue

		#if periodic and soft aperiodic task both exist
		if(len(soft_aprd) > 0 and len(period_tasks) > 0):

			#if a hard periodic task exists run it
			hrd_prd_tsk = get_hard_periodic_tsks(task_arr, has_executed)
			if(len(hrd_prd_tsk) > 0):
				task_to_execute = hrd_prd_tsk[0]
				for j in range(len(hrd_prd_tsk)):
					if hrd_prd_tsk[j].get_deadline(i) < task_to_execute.get_deadline(i):
						task_to_execute = hrd_prd_tsk[j]
				sr.add_instance(i, task_to_execute)
				deduct_unit_of_execution(task_to_execute, task_arr, has_executed, time_left)
				continue

			#else calculate slack between nearest periodic task and nearest aperiodic task to run			
			nearest_prd_tsk = period_tasks[0]
			nearest_apr_tsk = soft_aprd[0]

			for j in range(len(period_tasks)):
				if(period_tasks[j].get_deadline(i) < nearest_prd_tsk.get_deadline(i)):
					nearest_prd_tsk = period_tasks[j]

			for j in range(len(soft_aprd)):
				if(soft_aprd[j].get_deadline() < nearest_apr_tsk.get_deadline()):
					nearest_apr_tsk = soft_aprd[j]

			#use slack to pick which one will execute
			slack_et = nearest_apr_tsk.get_deadline() - (i + nearest_apr_tsk.get_comp_time())
			slack_pd = (nearest_prd_tsk.get_deadline(i) - (i + nearest_prd_tsk.get_comp_time())) * 2

			if(slack_et >= slack_pd):
				#execute periodic task
				sr.add_instance(i, nearest_prd_tsk)
				deduct_unit_of_execution(nearest_prd_tsk, task_arr, has_executed, time_left)
				continue
			else:
				sr.add_instance(i, nearest_apr_tsk)
				deduct_unit_of_execution(nearest_apr_tsk, task_arr, has_executed, time_left)
				continue

		#if there are only periodic tasks run hard else run soft
		ph_tasks = get_hard_periodic_tsks(task_arr, has_executed)
		if(len(ph_tasks) > 0):
			task_to_execute = ph_tasks[0]
			for j in range(len(ph_tasks)):
				if ph_tasks[j].get_deadline(i) < task_to_execute.get_deadline(i):
					task_to_execute = ph_tasks[j]
			sr.add_instance(i, task_to_execute)
			deduct_unit_of_execution(task_to_execute, task_arr, has_executed, time_left)
			continue
		else:
			ps_tasks = get_soft_periodic_tsks(task_arr, has_executed)
			if(len(ps_tasks) > 0):
				task_to_execute = ps_tasks[0]
				for j in range(len(ps_tasks)):
					if ps_tasks[j].get_deadline(i) < task_to_execute.get_deadline(i):
						task_to_execute = ps_tasks[j]
			sr.add_instance(i, task_to_execute)
			if task_to_execute != None:
				deduct_unit_of_execution(task_to_execute, task_arr, has_executed, time_left)

	sr.count_aperiodic_misses(time_left)

	return sr

# earliest deadline first will execute
def edf_scheduler(task_arr, time):

	sr = schedule_report(time, task_arr, False)

	has_executed = [False for i in range(len(task_arr))]
	time_left = [0 for i in range(len(task_arr))]

	for i in range(time):

		task_to_execute = None

		# reset task comp times and executed flags
		for j in range(len(task_arr)):
			#update task information if it just arrived such as time left to execute and is finished
			if(task_arr[j].is_periodic() and (i == 0 or i % task_arr[j].get_period() == 0)):
				if time_left[j] != 0:
					sr.missed_instance(task_arr[j])
				has_executed[j] = False # must be reset each time it arrives
				time_left[j] = task_arr[j].get_comp_time()

			if(task_arr[j].is_periodic() == False and task_arr[j].get_arr_time() == i):
				time_left[j] = task_arr[j].get_comp_time()

		# form a list with all possible tasks
		tasks_to_choose_from = []
		for j in range(len(task_arr)):
			if task_arr[j].is_periodic() == True:
				if time_left[j] > 0:
					tasks_to_choose_from.append(task_arr[j])
			else:
				#task is aperiodic
				if task_arr[j].get_arr_time() <= i and time_left[j] > 0:
					# if the task is hard and has missed deadline give up on it
					if task_arr[j].get_deadline_type() == "hard" and task_arr[j].get_deadline() <= i:
						print("cant add")
						continue;
					else:
						tasks_to_choose_from.append(task_arr[j])
						print("adding task")

		print("time {0}\n{1}".format(i, tasks_to_choose_from))



# auto generates a list of tasks for algorithms to schedule
def generate_task_list(periodic_utilization, aperiodic_utilization, hard_periodic_percent, hard_aperiodic_percent):
	# seeking 70% periodic task utilization and <30% aperiodic unless overload then >30%
	# 50% periodic tasks will be urgent "hard" and 50% will be "soft" or non urgent

	task_list = []
	utilization = 0.0

	while True:
		# 1% to 20% utilization on tasks
		computation_time = random.randint(1, 5)
		period_time = random.randint(25, 100)
		deadline_type = None

		# 50% chance of hard or soft
		if random.random() < hard_periodic_percent:
			deadline_type = "hard"
		else:
			deadline_type = "soft"

		#make sure not to go over utilization
		if computation_time / period_time + utilization > periodic_utilization:
			continue

		task_list.append(periodic_task(computation_time, period_time, deadline_type))
		utilization += computation_time / period_time

		#if utilization is atleast 68.5 % periodic tasks then that is enough
		if utilization >= periodic_utilization - 0.015:
			break
			# print("task list generated with utilization {0}".format(utilization))
			# return task_list

	#add aperiodic tasks to the list - will run 1000 time unit simulation
	while True:

		computation_time = random.randint(1, 10) # 1 - 10 units of computation
		arrival_time = random.randint(1, 950) # arrive such that all deadlines could be met
		deadline = arrival_time + 50 # deadline will be 20 time units after arrival
		deadline_type = "hard" if random.random() < hard_aperiodic_percent else "soft"

		task_list.append(aperiodic_task(arrival_time, computation_time, deadline, deadline_type))
		# max utilization an aperiodic task can add is 10/1000 or 1.0 %
		utilization += computation_time / 1000.0


		# utilization must be 1.05 to return the task list
		if utilization >= (periodic_utilization + aperiodic_utilization):
			print("task list generated with utilization {0}".format(utilization))
			return task_list

def test():
	#need to check example schedules to make sure algorithms work

	task_list = []

	task_list.append(periodic_task(1, 10, "soft"))
	task_list.append(periodic_task(1, 5, "soft"))
	task_list.append(aperiodic_task(0, 1, 10, "hard"))

	#RMS schedule check

	sched_rep = rms_scheduler(task_list, 10)
	# print(sched_rep)

	#FEF schedule check


	return True


def main():
	
	random.seed()

	if test() == True:
		print("Tests Passed")

	a = generate_task_list(0.5, 0.3, 0.5, 0.5)
	# print(a)



	task_list = []
	task_list.append(periodic_task(1, 6, "soft"))
	task_list.append(periodic_task(1, 5, "soft"))
	task_list.append(periodic_task(1, 4, "soft"))
	task_list.append(aperiodic_task(3, 10, 20, "hard"))
	# task_list.append(periodic_task(1, 3))
	# task_list.append(periodic_task(1, 4))

	# sched_rep = rms_scheduler(a, 1000)
	# print(sched_rep)

	# sched_rep = fair_emergency_scheduler(a, 1000)
	# print(sched_rep)

	edf_scheduler(task_list, 25)

	

if __name__ == "__main__":
	main()