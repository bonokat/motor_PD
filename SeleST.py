"""
Selective Stopping Toolbox (SeleST)
    Written by Corey Wadsley*,** with help from Fenwick Nolan
        *Movement Neuroscience Laboratory, Department of Exercise Sciences, The University of Auckland
        **Action Control Laboratory, Department of Human Physiology, University of Oregon
    
    Last updated: 23-Feb-2024
    Further information can be found at:
        https://github.com/coreywadsley/SeleST
    
    If you use this task, please cite:
    Wadsley, C. G., Cirillo, J., Nieuwenhuys, A., & Byblow, W. D. (2023). Comparing anticipatory and stop-signal 
    response inhibition with a novel, open-source selective stopping toolbox, Exp Brain Res. DOI: 10.1007/s00221-022-06539-9

    If you have any issues, feel free to contact Corey at:
        cwadsley@uoregon.edu
"""

# Some general housekeeping before we start
# import required modules
import os
from psychopy import core
from lib import SeleST_initialize, SeleST_run
# NEW!
from psychopy.hardware import keyboard

# ensure that the relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(_thisDir)

#   ---SeleST_initialize---
# Here we are initializing all of the information that can change across sessions 
    # additional info for each class can be found in the SeleST_initialize script
exp = SeleST_initialize.Experiment(_thisDir) # exp class
stimuli = SeleST_initialize.Stimuli(exp) # stimuli class 
trialInfo = SeleST_initialize.Trials(exp) # trialInfo class
stopInfo = SeleST_initialize.SSD(exp) # stopInfo class
# NEW!
exp.rb = keyboard.Keyboard()
#allKeys = exp.rb.getKeys(keyList=['1','2','space'], waitRelease=False)

#   ---SeleST_run---
# Here we are running the task by looping over blocks and trials
    # additional info for each function can be found in the SeleST_run script
for thisBlock in trialInfo.blockList: # iterate over blocks
    print(trialInfo)
#    exp.rb = keyboard.Keyboard() #! NEW
#    allKeys = exp.rb.getKeys(keyList=['1','2','space'], waitRelease=False) #! NEW
    thisBlockTrials = SeleST_run.Block(exp, trialInfo) # process trials in the current block
    
    for trial in thisBlockTrials: # iterate over trials in the current block
        trialInfo.trialCount = trialInfo.trialCount + 1 # track trial number
        thisTrial = SeleST_run.Initialize_trial(exp, trialInfo, stopInfo, trial) # set parameters of current trial
        print('Trial number %s'%(trialInfo.trialCount) + ' - ' + thisTrial.trialName) # print trial number & name to console
        trialStimuli = SeleST_run.Start_Trial(exp,stimuli,trialInfo,thisTrial,trial) # set additional trial related parameters
        SeleST_run.pd_trig(exp, trialStimuli) # photodiode trigger for start of trial
        if exp.advSettings['Send serial trigger at trial onset?'] == True: # serial trigger for trial start            
#            exp.ser.write('WRITE 1 5000 0\n'.encode('utf-8'))
            trigger_code = 1
            exp.ser.write(f"WRITE {trigger_code} 5000 0\n".encode("utf-8"))
            timestamp = exp.trialClock.getTime()
            exp.trigger_log.write(
                f"{timestamp:.6f}\t{trialInfo.trialCount}\t{thisTrial.trialName}\t{trigger_code}\n"
            )
            exp.trigger_log.flush()

        fixPeriod = SeleST_run.fixationPeriod(exp,stimuli,trialStimuli) # run fixation period
        if exp.taskInfo['Response mode'] == 'Wait-and-press': # clear events in buffer if wait-and-press version
            exp.rb.clearEvents()
        startTime = round(exp.globalClock.getTime(),1) # record trial start time and print it to the console
        print('Trial started at %s seconds'%startTime)
        trialTimer = core.CountdownTimer(exp.advSettings['Trial length (s)']) # set trial timer
        stopTimer = core.CountdownTimer(thisTrial.stopTime/1000) # set stop timer
        exp.win.callOnFlip(exp.rb.clock.reset)
        if exp.advSettings['Send serial trigger at trial onset?'] == True: # serial trigger for trial start (bar starts filling)            
#            exp.ser.write('WRITE 2 5000 0\n'.encode('utf-8'))   
            trigger_code = 2
            exp.ser.write(f"WRITE {trigger_code} 5000 0\n".encode("utf-8"))
            timestamp = exp.trialClock.getTime()
            exp.trigger_log.write(
                f"{timestamp:.6f}\t{trialInfo.trialCount}\t{thisTrial.trialName}\t{trigger_code}\n"
            )
            exp.trigger_log.flush()
        while trialTimer.getTime() > 0: # run trial while timer is positive
            SeleST_run.runTrial(exp,stimuli,thisTrial,trialStimuli,trialTimer)
            if stopTimer.getTime() <= 0: # present stop signal when stop timer reaches 0                
                SeleST_run.stop_signal(exp,stimuli,thisTrial,trialStimuli)
            exp.win.flip() # update stimuli on every frame
        SeleST_run.getRT(exp, thisTrial, trialStimuli) # get RTs for current trial
        SeleST_run.feedback(exp, stimuli, trialInfo, thisTrial, trialStimuli) # calculate response accuracy and present feedback
        SeleST_run.staircaseSSD(exp, stopInfo, thisTrial) # staircase SSD if applicable
        SeleST_run.saveData(exp, trialInfo, thisTrial, startTime) # save data from current trial
        SeleST_run.pd_trig(exp, trialStimuli)
        if exp.advSettings['Send serial trigger at trial onset?'] == True: # serial trigger for trial end            
#            exp.ser.write('WRITE 6 5000 0\n'.encode('utf-8'))
            trigger_code = 6
            exp.ser.write(f"WRITE {trigger_code} 5000 0\n".encode("utf-8"))
            timestamp = exp.trialClock.getTime()
            exp.trigger_log.write(
                f"{timestamp:.6f}\t{trialInfo.trialCount}\t{thisTrial.trialName}\t{trigger_code}\n"
            )
            exp.trigger_log.flush()

        SeleST_run.ITI(exp, stimuli, trialStimuli) # end trial and run the intertrial interval
    SeleST_run.endBlock(exp, trialInfo, thisBlockTrials) # calculate block score and present end-of-block feedback
SeleST_run.endTask(exp, stimuli, trialStimuli) # end the task when all blocks have been completed
