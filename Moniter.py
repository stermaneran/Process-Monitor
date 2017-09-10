import psutil
import time
import os
from shutil import copy
from sys import argv
from hashlib import md5 as md5
from multiprocessing import Process as proc
from random import randint as rand

try:
    os.makedirs("folder")
except OSError:
    pass

tmp = open("./folder/tmp.txt", "w")
ans = open("./folder/ans.txt", "w")
mem_monitor = {}
num_for_mem_check = 5
coder_num = rand(0, 9)


def my_coder(line):
    lines = list(line)
    code = ""
    for i in range(len(lines)):
        if lines[i] == "\n":
            code += '\n'
            continue
        ch = ord(lines[i]) + coder_num
        code += chr(ch)
    return code


def my_decoder(line):
    lines = list(line)
    code = ""
    for i in range(len(lines)):
        if lines[i] == "\n":
            code += '\n'
            continue
        ch = ord(lines[i]) - coder_num
        code += chr(ch)
    return code


def decode(name):
    try:
        with open("./folder/ans.txt", "w") as a:
            copy(name, "./folder/tmp.txt")
            ff = open("./folder/tmp.txt", "r")
            for line in ff:
                a.write(my_decoder(line))
            tmp.close()
            ans.close()
        if os.name == 'nt':
            with open("./folder/ans.txt", "r") as a:
                print (a.read())
        else:
            os.system("open ./folder/ans.txt")
    except IOError:
        pass


def dater(b=False):
    date = time.strftime("%d/%m/%Y")
    hour = time.strftime("%H:%M:%S")
    if b:
        with open("./folder/dates.txt", "a") as ff:
            ff.write(my_coder(date + " " + hour))
            ff.write('\n')
    return "\n{} {}\n".format(date, hour)


def binary_search(sequence, value):
    lo, hi = 0, len(sequence) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sequence[mid].get_pid() < value:
            lo = mid + 1
        elif value < sequence[mid].get_pid():
            hi = mid - 1
        else:
            return mid
    return None


def insertion(array):
    for i in range(1, len(array)):
        j = i
        while j > 0 and array[j].get_pid() < array[j - 1].get_pid():
            array[j], array[j - 1] = array[j - 1], array[j]
            j = j - 1
    return array


class MyProcess:
    def __init__(self, name, pid, ram):
        self.name = name
        self.pid = pid
        self.ram = ram
        self.children = []

    def get_name(self):
        return self.name

    def get_ram(self):
        return self.ram

    def get_pid(self):
        return self.pid

    def get_children(self):
        return self.children

    def add_child(self, child):
        self.children.append(child)
        self.children = insertion(self.children)

    def check(self, children):
        if binary_search(children, self.get_pid()) is not None:
            return True
        return False


def update():
    s = ""
    temp = []
    s += (my_coder(dater(True)))
    for p in psutil.process_iter():
        try:

            if p.name() not in mem_monitor:
                mem_monitor[p.name()] = [p.memory_percent(), 0, 0]
            else:
                if mem_monitor[p.name()][2] < num_for_mem_check and mem_monitor[p.name()][0] != "Root":
                    mem_monitor[p.name()][1] = max(mem_monitor[p.name()][1], abs(p.memory_percent() -
                                                                                 mem_monitor[p.name()][0]))
                    mem_monitor[p.name()][2] += 1
                    mem_monitor[p.name()][0] = (mem_monitor[p.name()][0] +
                                                p.memory_percent()) / (mem_monitor[p.name()][2] + 1)
            args = "Name: {0:40}\tPid:{1:5}\tMem:{2:25}\n".format(p.name(), str(p.pid), str(p.memory_percent()))
            s += my_coder(args)
            process = MyProcess(p.name(), p.pid, str(p.memory_percent()))

        except psutil.AccessDenied:
            if p.name() not in mem_monitor:
                mem_monitor[p.name()] = ["Root", 0, 0]
            args = "Name: {0:40}\tPid:{1:5}\tMem:Root\n".format(p.name(), str(p.pid))
            s += my_coder(args)
            process = MyProcess(p.name(), p.pid, "Root")

        try:

            for ch in p.children():
                child = ch.as_dict(attrs=["pid", "name", "memory_info"])
                process.add_child(MyProcess(child["name"], child["pid"], child["memory_info"]))

        except psutil.NoSuchProcess:
            pass

        temp.append(process)

    with open("./folder/processList.txt", "a") as processList:
        processList.write(s)
        processList.write(my_coder("end"))
    return temp


def compare(old_sorted, new_sorted, boo=True):
    s = ""
    first = boo
    i = j = 0
    while i < len(new_sorted) or j < len(old_sorted):
        if i == len(new_sorted):
            if first:
                s += (dater())
                first = False

            s += ("**process died** {0:40} Pid:{1:10}\n".format(old_sorted[j].get_name(), str(old_sorted[j].get_pid())))
            j += 1
            continue

        if j == len(old_sorted):
            if first:
                s += (dater())
                first = False
            s += ("!!new process!!  {0:40} Pid:{1:10}\n".format(new_sorted[i].get_name(), str(new_sorted[i].get_pid())))
            i += 1
            continue

        if str(new_sorted[i].get_pid()) < str(old_sorted[j].get_pid()):
            if first:
                s += (dater())
                first = False
            s += ("!!new process!!  {0:40} Pid:{1:10}\n".format(new_sorted[i].get_name(), str(new_sorted[i].get_pid())))
            i += 1
            continue

        if str(new_sorted[i].get_pid()) > str(old_sorted[j].get_pid()):
            if first:
                s += (dater())
                first = False
            s += ("**process died** {0:40} Pid:{1:10}\n".format(old_sorted[j].get_name(), str(old_sorted[j].get_pid())))
            j += 1
            continue

        for process in new_sorted[i].get_children():
            if not process.check(old_sorted[j].get_children()):
                if first:
                    s += (dater())
                    first = False
                s += ("process {0} has new child: {1:26} Pid:{2:10}\n".format
                      (new_sorted[i].get_name(), process.name, str(process.get_pid())))

        try:

            if mem_monitor[old_sorted[j].get_name()][2] == 5 and mem_monitor[old_sorted[j].get_name()][0] != "Root" \
                    and new_sorted[i].get_ram() != "Root" and old_sorted[j].get_ram() != "Root":
                if abs(float(new_sorted[i].get_ram()) - float(old_sorted[j].get_ram())) > \
                        (mem_monitor[new_sorted[i].get_name()][1] * 2):
                    event = ("\nprocess {0} memory use is not avg\navg={1:5}\nnow:{2:25}\n".format
                             (new_sorted[i].get_name(), str(mem_monitor[new_sorted[i].get_name()][1]),
                              str(new_sorted[i].get_ram())))
                    mem_monitor[new_sorted[i].get_name()][1] = \
                        float(new_sorted[i].get_ram()) - float(old_sorted[j].get_ram())
                    with open("./folder/Status_Log.txt", "a+") as o:
                        o.write(my_coder(event))
                        print (event)

        except KeyError:
            pass
        except ValueError:
            pass

        i += 1
        j += 1

    return s


def scan(old):
    old_sorted = insertion(old)
    new_sorted = update()
    new_sorted = insertion(new_sorted)
    event = compare(old_sorted, new_sorted)
    if event != "":
        with open("./folder/Status_Log.txt", "a+") as o:
            o.write(my_coder(event))
            print (event)

    old = new_sorted
    return old


def runner(sleeper):
    old = update()
    while True:
        time.sleep(sleeper)

        old = scan(old)


def get_samples(time1, time2):
    b = False
    old_sorted = []
    new_sorted = []
    with open("./folder/processList.txt") as f:
        for l in f:
            line = l
            if time1 in line or b:
                b = True
                if line.strip() == my_coder("end"):
                    break

                n = line.find(my_coder("Name:"))
                p = line.find(my_coder("Pid:"))
                m = line.find(my_coder("Mem:"))
                if n != -1 and p != -1 and m != -1:
                    name = my_decoder(line[n + 6:p - 1])
                    pid = my_decoder(line[p + 5:m - 1])
                    mem = my_decoder(line[m + 5:])
                    pro = MyProcess(name, pid, mem)
                    old_sorted.append(pro)

    b = False
    with open("./folder/processList.txt") as f:
        for l in f:
            line = l
            if time2 in line or b:
                b = True
                if line.strip() == my_coder("end"):
                    break

                n = line.find(my_coder("Name:"))
                p = line.find(my_coder("Pid:"))
                m = line.find(my_coder("Mem:"))
                if n != -1 and p != -1 and m != -1:
                    name = my_decoder(line[n + 6:p - 1])
                    pid = my_decoder(line[p + 5:m - 1])
                    mem = my_decoder(line[m + 5:])
                    pro = MyProcess(name, pid, mem)
                    new_sorted.append(pro)

    old_sorted = insertion(old_sorted)
    new_sorted = insertion(new_sorted)

    if len(old_sorted) != 0 and len(new_sorted) != 0:
        with open("./folder/ans.txt", "w") as a:
            s = "\nyour request from samples{0:40} - {1:40}\n\n{2:40}".\
                format(my_decoder(time1), my_decoder(time2), compare(old_sorted, new_sorted, False))
            a.write(str(s))
            a.close()
        if os.name == 'nt':
            with open("./folder/ans.txt", "r") as a:
                print (a.read())
        else:
            os.system("open ./folder/ans.txt")

    else:
        with open("./folder/ans.txt", "w") as a:
            a.write("\nyour request from samples{0:40} - {1:40}\n\n".format(my_decoder(time1), my_decoder(time2)))
            a.close()
        if os.name == 'nt':
            with open("./folder/ans.txt", "r") as a:
                print (a.read())
        else:
            os.system("open ./folder/ans.txt")


def d():
    with open("./folder/dates.txt", "r+") as ff:
        dd = ff.read().split()
    if len(dd) > 2:
        print ("choose date from list:")
        for i in range(len(dd) - 1):
            print (str(i + 1) + ") " + my_decoder(dd[i]))
        try:

            t1 = input("\nfirst date?")
            t2 = input("second date?")
            if 0 < t1 and t2 < (len(dd)):
                get_samples(dd[int(t1) - 1], dd[int(t2) - 1])
            else:
                print ("invalid input!!!")

        except NameError:
            print ("invalid input!!!")
        except SyntaxError:
            print ("invalid input!!!")

    else:
        print ("not enough data yet...\n")


def v():
    klt = raw_input("\nenter:\ns to view Status_Log\np to view ProcessList\nr to return\n")

    if klt == 'p':
        decode('./folder/processList.txt')
        return

    if klt == 's':
        decode('./folder/Status_Log.txt')
        return


def test_hashes():
    try:

        h2 = md5(open("./folder/processList.txt", 'rb').read()).hexdigest()

        try:
            h1 = md5(open("./folder/Status_Log.txt", 'rb').read()).hexdigest()
        except IOError:
            h1 = ""

        with open("./folder/Hashes.txt", "r+") as ff:
            hashes = ff.read()
            h = hashes.split('\n')

        if h[0] != h2:
            print ("processList file compromised!!!")
        if h[1] != h1:
            print ("Status_Log file compromised!!!")
    except IOError:
        pass


def encrypt():
    try:
        with open("./folder/Status_Log.txt", "r+") as ff:
            with open("./folder/tmp.txt", "w") as a:
                for line in ff:
                    a.write(my_coder(line))
            tmp.close()
            copy("./folder/tmp.txt", "./folder/Status_Log.txt")
    except IOError:
        pass

    try:
        with open("./folder/processList.txt", "r+") as ff:
            with open("./folder/tmp.txt", "w") as a:
                for line in ff:
                    a.write(my_coder(line))
            tmp.close()
            copy("./folder/tmp.txt", "./folder/processList.txt")
    except IOError:
        pass

    try:
        with open("./folder/dates.txt", "r+") as ff:
            with open("./folder/tmp.txt", "w") as a:
                for line in ff:
                    a.write(my_coder(line))
            tmp.close()
            copy("./folder/tmp.txt", "./folder/dates.txt")
    except IOError:
        pass


def decrypt():
    try:
        with open("./folder/processList.txt", "r+") as ff:
            with open("./folder/tmp.txt", "w") as a:
                for line in ff:
                    a.write(my_decoder(line))
                tmp.close()
                copy("./folder/tmp.txt", "./folder/processList.txt")
    except IOError:
        pass

    try:
        with open("./folder/Status_Log.txt", "r+") as ff:
            with open("./folder/tmp.txt", "w") as a:
                for line in ff:
                    a.write(my_decoder(line))
            tmp.close()
            copy("./folder/tmp.txt", "./folder/Status_Log.txt")
    except IOError:
        pass

    try:
        with open("./folder/dates.txt", "r+") as ff:
            with open("./folder/tmp.txt", "w") as a:
                for line in ff:
                    a.write(my_decoder(line))
            tmp.close()
            copy("./folder/tmp.txt", "./folder/dates.txt")
    except IOError:
        pass


def get_hashes():
    try:
        with open("./folder/Hashes.txt", "w+") as ff:
            ff.write(md5(open("./folder/processList.txt", 'rb').read()).hexdigest())
            ff.write('\n')
    except IOError:
        pass

    try:
        with open("./folder/Hashes.txt", "a+") as ff:
            ff.write(md5(open("./folder/Status_Log.txt", 'rb').read()).hexdigest())
    except IOError:
        pass

options = {'d': d,
           'v': v,
           }


def main():
    try:
        if os.name == 'posix':
            if os.geteuid() != 0:
                print ("must run with root privileges!\ntry sudo{} ".format(str(argv[0])))
                return
        test_hashes()
        encrypt()
        sleeper = raw_input("enter secs for check:")
        while not sleeper.isdigit() or sleeper < str(0):
            print ("invalid input")
            sleeper = raw_input("enter secs for check:")

        th = proc(target=runner, args=(int(sleeper), ))
        th.start()
        print ("the scans are running...\n")
        user = raw_input("enter:\nd to test dates\nv to view files\nq to quit\n")
        while user != 'q':
            if user == 'd' or user == "v":
                options[user]()
            user = raw_input("enter:\nd to test dates\nv to view files\nq to quit\n")

        print ("quiting program")
        th.terminate()
        while th.is_alive():
            time.sleep(0.01)

        decrypt()

        ans.close()
        tmp.close()
        os.remove("./folder/ans.txt")
        os.remove("./folder/tmp.txt")

        get_hashes()
    except:
        print"unexpected error quiting"
        try:
            if th.is_alive():
                th.terminate()
        except:
            pass
    print ("Bye Bye!")


if __name__ == '__main__':
    main()
