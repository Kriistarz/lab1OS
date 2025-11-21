import ctypes  # Низкоуровневое обращение к DLL и структурам C
import getpass  # Для имени текущего пользователя
import os  # Для общих утилит
import platform  # Для определения версии/релиза ОС
import socket  # Для получения имени хоста

import win32api  # Обёртки pywin32 для простых вызовов Win32 API
import win32file  # Для функций файловой системы (сведения о дисках)


def get_os_version():
    """Функция определения версии ос."""
    rel = platform.release()  # Возвращает строку с номером версии
    if "10" in rel or "11" in rel:
        return "Windows 10 or Greater"
    elif rel == "8.1":
        return "Windows 8.1"
    elif rel == "8":
        return "Windows 8"
    elif rel == "7":
        return "Windows 7"
    else:
        return f"Older than Windows 7 ({rel})"


def get_architecture():
    """Функция определения архитектуры процессора."""
    # Возвращает информацию о системе, включая архитектуру процессора
    si = win32api.GetNativeSystemInfo()
    arch_code = si[0]  # Первый элемент - архитектура
    if arch_code == 9:  # Сравниваем код с константами архитектур и возвращаем название
        return "x64 (AMD64)"
    elif arch_code == 0:
        return "x86"
    elif arch_code == 12:
        return "ARM64"
    else:
        return "Unknown"


class MEMORYSTATUSEX(ctypes.Structure):
    """Структура для информации о памяти."""
    # Список полей структуры
    _fields_ = [
        ("dwLength", ctypes.c_ulong),  # размер структуры в байтах
        ("dwMemoryLoad", ctypes.c_ulong),  # процент использования памяти
        ("ullTotalPhys", ctypes.c_ulonglong),  # общий физический RAM
        ("ullAvailPhys", ctypes.c_ulonglong),  # доступная физическая память
        ("ullTotalPageFile", ctypes.c_ulonglong),  # общий размер файла подкачки
        ("ullAvailPageFile", ctypes.c_ulonglong),  # доступный pagefile
        ("ullTotalVirtual", ctypes.c_ulonglong),  # общий виртуальный адресный объем
        ("ullAvailVirtual", ctypes.c_ulonglong),  # доступный виртуальный адрес
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]
def print_memory_info():
    """Функция получения информации о памяти."""
    meminfo = MEMORYSTATUSEX()
    meminfo.dwLength = ctypes.sizeof(meminfo)  # Заполняем поле размера структуры (это требование Windows API)
    # Вызываем функцию GlobalMemoryStatusEx из kernel32.dll, передавая указатель на нашу структуру
    res = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(meminfo))
    if not res:
        # Если вызов вернул 0 - ошибка
        print("Failed to get memory info via GlobalMemoryStatusEx.")
        return

    # Переводим байты в мегабайты
    total_phys = meminfo.ullTotalPhys // (1024 * 1024)
    avail_phys = meminfo.ullAvailPhys // (1024 * 1024)
    total_page = meminfo.ullTotalPageFile // (1024 * 1024)
    load = meminfo.dwMemoryLoad  # Процент использования памяти
    # Вычисляем использованную память и выводим информацию
    used_mb = total_phys - avail_phys
    print(f"RAM: {used_mb}MB / {total_phys}MB")
    print(f"Virtual Memory: {total_page}MB")
    print(f"Memory Load: {load}%")


class PERFORMANCE_INFORMATION(ctypes.Structure):
    """Структура для расширенной информации о производительности."""
    _fields_ = [
        ("cb", ctypes.c_ulong),  # размер структуры в байтах
        ("CommitTotal", ctypes.c_size_t),
        ("CommitLimit", ctypes.c_size_t),
        ("CommitPeak", ctypes.c_size_t),
        ("PhysicalTotal", ctypes.c_size_t),
        ("PhysicalAvailable", ctypes.c_size_t),
        ("SystemCache", ctypes.c_size_t),
        ("KernelTotal", ctypes.c_size_t),
        ("KernelPaged", ctypes.c_size_t),
        ("KernelNonpaged", ctypes.c_size_t),
        ("PageSize", ctypes.c_size_t),  # размер страницы в байтах
        ("HandleCount", ctypes.c_ulong),
        ("ProcessCount", ctypes.c_ulong),
        ("ThreadCount", ctypes.c_ulong),
    ]


def print_pagefile_info():
    """Функция информации о файле подкачки."""
    perf = PERFORMANCE_INFORMATION()
    perf.cb = ctypes.sizeof(perf)
    ok = ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(perf), perf.cb)
    # Вычисляем общий и использованный объем файла подкачки в МБ
    if ok:
        total_pagefile_mb = (perf.CommitLimit * perf.PageSize) // (1024 * 1024)
        used_pagefile_mb = (perf.CommitTotal * perf.PageSize) // (1024 * 1024)
        print(f"Pagefile: {used_pagefile_mb}MB / {total_pagefile_mb}MB")
    else:
        print("Failed to get pagefile info (GetPerformanceInfo failed).")


def print_drive_info():
    """Функция информации о дисках."""
    drives_str = win32api.GetLogicalDriveStrings()  # Получаем строку с перечнем всех логических дисков
    drives = drives_str.split('\x00')[:-1]  # Разделяем строку по нулевым символам и убираем последний пустой элемент
    # Для каждого диска получаем информацию о свободном и общем месте
    print("Drives:")
    for d in drives:
        try:
            free, total, free2 = win32file.GetDiskFreeSpaceEx(d)
            # Байты в ГБ
            free_gb = free // (1024 ** 3)
            total_gb = total // (1024 ** 3)
            print(f"  - {d}: {free_gb} GB free / {total_gb} GB total")
        except Exception as e:
            print(f"  - {d}: error ({e})")


def main():
    # OS
    print(f"OS: {get_os_version()}")

    try:
        computer_name = win32api.GetComputerName()
    except Exception:
        # Если win32api недоступен, используем socket
        computer_name = socket.gethostname()
    print(f"Computer Name: {computer_name}")

    try:
        user_name = win32api.GetUserName()
    except Exception:
        user_name = getpass.getuser()
    print(f"User: {user_name}")

    # Архитектура
    print(f"Architecture: {get_architecture()}")
    # Получаем количество процессоров
    si = win32api.GetSystemInfo()
    proc_count = None
    try:
        proc_count = si[5]
    except Exception:
        proc_count = os.cpu_count()
    print(f"Processors: {proc_count}")

    # Вывод остальной информации
    print_memory_info()
    print_pagefile_info()
    print_drive_info()


if __name__ == "__main__":
    main()
