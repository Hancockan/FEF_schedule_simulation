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
		return "({0}, {1}) {2}".format(self.comp_time, self.period, str(self.id))

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

	def get_id(self):
		return self.id

	def __str__(self):
		return str(self.id)

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
	tsklist = []
	for i in range(len(task_arr)):
		if(task_arr[i].is_periodic() and has_executed[i] == False):
			tsklist.append(task_arr[i])
	return tsklist

#check if soft aperiodic tasks exist
def get_aperiodic_soft(task_arr, has_executed, time):
	tsklist = []
	for i in range(len(task_arr)):
		if(task_arr[i].is_periodic() == False and has_executed[i] == False and task_arr[i].get_arr_time() <= time):
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

def deduct_unit_of_execution(task, task_arr, has_executed, time_left):
	for i in range(len(task_arr)):
		if task.get_id() == task_arr[i].get_id():
			time_left[i] = time_left[i] - 1
			if time_left[i] < 1:
				has_executed[i] = True
			return


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

		#need to reset all task stats 
		for j in range(len(task_arr)):
			
			#update task information if it just arrived such as time left to execute and is finished
			if(task_arr[j].is_periodic() and (i == 0 or i % task_arr[j].get_period() == 0)):
				has_executed[j] = False
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
	return sr


"""

"""
def test_1():
	task_list = []
	task_list.append(periodic_task(1, 10, "soft"))



def main():
	
	task_list = []
	task_list.append(periodic_task(1, 4, "soft"))
	task_list.append(aperiodic_task(0, 1, 6, "hard"))
	task_list.append(aperiodic_task(0, 1, 6, "soft"))
	# task_list.append(periodic_task(1, 3))
	# task_list.append(periodic_task(1, 4))


	sched_rep = rms_scheduler(task_list, 20)
	print(sched_rep)

	sched_rep = fair_emergency_scheduler(task_list, 20)
	print(sched_rep)


	print(uuid.uuid1())

if __name__ == "__main__":
	main()



