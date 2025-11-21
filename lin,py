import os
import platform
import getpass
import socket

def get_os_info():
    """Получает информацию о дистрибутиве Linux, читая файл /etc/os-release."""
    distro = "Unknown"
    try:
        # /etc/os-release содержит поля NAME="Ubuntu" VERSION="22.04"
        with open("/etc/os-release") as f:
            info = {}
            for line in f:
                # Обрабатываем строки вида KEY=VALUE
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    info[key] = val.strip('"')  # убираем кавычки
            # Формируем строку вида "Ubuntu 22.04"
            distro = f"{info.get('NAME', '')} {info.get('VERSION', '')}".strip()
    except Exception:
        # Если файла нет (например, не Linux) — возвращаем Unknown
        pass
    return distro


def get_memory_info():
    """Читает файл /proc/meminfo и возвращает объём памяти в МБ.
    Возвращает:
        total — общая RAM
        free — доступная RAM
        swap_total — общий swap
        swap_free — свободный swap
        virtual — общий Vmalloc (виртуальная память ядра)
    """
    meminfo = {}

    # /proc/meminfo содержит строки вида: "MemTotal: 16384256 kB"
    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":")
            # Берем только численное значение в КБ
            meminfo[key.strip()] = int(value.strip().split()[0])

    # Преобразуем значения из КБ в МБ
    total = meminfo.get("MemTotal", 0) // 1024
    free = meminfo.get("MemAvailable", meminfo.get("MemFree", 0)) // 1024
    swap_total = meminfo.get("SwapTotal", 0) // 1024
    swap_free = meminfo.get("SwapFree", 0) // 1024
    virtual = meminfo.get("VmallocTotal", 0) // 1024

    return total, free, swap_total, swap_free, virtual


def get_load_average():
    """Возвращает среднюю загрузку системы за 1, 5 и 15 минут.
    Читает /proc/loadavg."""
    with open("/proc/loadavg") as f:
        return f.read().strip().split()[:3]  # берем первые три числа


def get_drives_info():
    """Возвращает список подключённых файловых систем (только реальных),
    включая свободное и общее место.

    Фильтруются только ext4 и devpts, чтобы исключить виртуальные и системные FS.
    """
    drives = []
    seen = set()
    allowed_fs = ("ext4", "devpts")  # разрешённые типы файловых систем

    with open("/proc/mounts") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 3:
                device, mountpoint, fstype = parts[:3]

                # исключаем нежелательные типы ФС
                if fstype not in allowed_fs:
                    continue

                # избегаем дублирования
                if mountpoint in seen:
                    continue
                seen.add(mountpoint)

                try:
                    # Получаем статистику файловой системы
                    stats = os.statvfs(mountpoint)
                    total = (stats.f_blocks * stats.f_frsize) / (1024**3)
                    free = (stats.f_bavail * stats.f_frsize) / (1024**3)
                    drives.append((mountpoint, fstype, free, total))
                except Exception:
                    continue

    return drives


def main():
    # Общая информация о системе
    os_info = get_os_info()
    kernel = f"{platform.system()} {platform.release()}"  # например Linux 6.8
    arch = platform.machine()  # архитектура CPU
    hostname = socket.gethostname()
    user = getpass.getuser()

    # Память
    total, free, swap_total, swap_free, virtual = get_memory_info()

    # Загрузка CPU
    load = get_load_average()
    processors = os.cpu_count()  # количество логических ядер

    # Диски
    drives = get_drives_info()

    # Вывод
    print(f"OS: {os_info}")
    print(f"Kernel: {kernel}")
    print(f"Architecture: {arch}")
    print(f"Hostname: {hostname}")
    print(f"User: {user}")
    print(f"RAM: {free}MB free / {total}MB total")
    print(f"Swap: {swap_total}MB total / {swap_free}MB free")
    print(f"Virtual memory: {virtual} MB")
    print(f"Processors: {processors}")
    print(f"Load average: {', '.join(load)}")
    print("Drives:")

    for mountpoint, fstype, free, total in drives:
        print(f"  {mountpoint:<10} {fstype:<7} {free:.0f}GB free / {total:.0f}GB total")


if __name__ == "__main__":
    main()
