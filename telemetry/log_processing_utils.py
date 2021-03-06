import os
import datetime
import subprocess
from pathlib import Path
from zipfile import ZipFile


class LogProcessing():
    def __init__(self, log_path, target, device_name, datetime_format, max_log_size, log_period):
        self.log_path = log_path
        self.target = target
        self.device_name = device_name
        self.datetime_format = datetime_format
        self.max_log_size = max_log_size
        self.log_period = log_period

        self.start_log_time = datetime.datetime.now()
        self.stop_log_time = self.start_log_time

    def samba_setup(self, samba_ip, samba_login, samba_password):
        self.samba_server_ip = samba_ip
        self.samba_login = samba_login
        self.samba_password = samba_password

    def check_logs_size(self):
        logs_size = 0

        for log in self.log_path.glob(f"{self.target}*"):
            logs_size += log.stat().st_size

        if logs_size > self.max_log_size:
            return True
        else:
            return False

    def archive_logs(self):
        print('time')
        if self.start_log_time == self.stop_log_time:
            self.stop_log_time = datetime.datetime.now()
        arhive_name = f"{self.log_path}/old_{self.target}.({self.start_log_time.strftime(self.datetime_format)}&{self.stop_log_time.strftime(self.datetime_format)}).zip"
        print(arhive_name)

        with ZipFile(arhive_name, 'w') as archive:
            for log in self.log_path.glob(f"{self.target}*"):
                archive.write(log, log.name)
                os.remove(log)

        if self.samba_server_ip and self.samba_login and self.samba_password:
            archives = list(self.log_path.glob(f"old_{self.target}*"))

            returncode = self.samba_log_upload(archives)
        else:
            print("Samba settings are incorrect")
            return

        if returncode:
            self.delete_old(delete='archive')

    def delete_old(self, delete='log', exceptions=[]):
        if delete == 'archive':
            olds = list(self.log_path.glob(f"old_{self.target}*"))
        elif delete == 'log':
            olds = list(self.log_path.glob(f"{self.target}*"))

        if len(olds) > 0:
            for archive in olds:
                os.remove(archive)

    def log_file_path_gen(self, device_ids):
        # Generate string paths to devices, like:
        # tpu0_Y-01-01_12-12-12.csv
        paths = []
        for device_id in device_ids:
            paths.append("{}/{}{}_{}.csv".format(self.log_path,
                                                  self.target,
                                                  device_id,
                                                  datetime.datetime.now().strftime(f"{self.datetime_format}")))
        return paths

    def check_old_logs(self):
        current_time = datetime.datetime.now()
        result = False

        for old_log in self.log_path.glob(f"{self.target}*"):
            file_time = old_log.stem
            # Divides the string according to the standard time format
            file_time = file_time.split('_')[1:]
            file_time = '_'.join(file_time)
            file_time = datetime.datetime.strptime(file_time, self.datetime_format)

            if file_time < self.start_log_time:
                self.start_log_time = file_time
            if file_time > self.stop_log_time:
                self.stop_log_time = file_time

            if file_time + datetime.timedelta(days=self.log_period) < current_time:
                result = True

        return result

    def samba_log_upload(self, input_files):
        if not isinstance(input_files, list):
            input_files = [input_files]

        for upload_file_name in input_files:
            if not isinstance(input_files, Path):
                upload_file_name = Path(upload_file_name)

            output_file = f"/telemetry/{self.device_name}/{upload_file_name.name}"
            load_files = subprocess.run("smbclient //{}/fssamba -U {}%{} -c 'mkdir /telemetry/{}; put {} {}'".format(self.samba_server_ip,
                                                                                                                     self.samba_login,
                                                                                                                     self.samba_password,
                                                                                                                     self.device_name,
                                                                                                                     upload_file_name,
                                                                                                                     output_file),
                                        shell=True)

            # returncode 0 - success, 1 - error
            if load_files.returncode:
                return False

        return True
