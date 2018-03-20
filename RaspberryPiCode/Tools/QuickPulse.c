/*
 *  The purpose of this file is to speed up the rate at which python can talk to the GPIO
 *  pins. If you are using the raspberry pi V2 or V3, you do not need to use this file.
 *
 *
 *  To get python to use this file, you need to get bcm2835 and compile this file
 *  To get bcm2835 use the following to download and install the tar.gz file:
 *  >>> wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.55.tar.gz
 *  >>> tar zxvf bcm2835-1.xx.tar.gz
 *  >>> cd bcm2835-1.xx
 *  >>> ./configure
 *  >>> make
 *  >>> sudo make check
 *  >>> sudo make install
 *
 *  To compile this file use:
 *  >>> gcc -shared -I/usr/include/python2.7 -lpython2.7 QuickPulse.c -o QuickPulse.so -l bcm2835
 */

#include <Python.h>

#include <bcm2835.h>

static PyObject *py_DoQuickPulse(PyObject* self, PyObject* args)
{
        int slkpin, datapin;
        PyArg_ParseTuple(args, "ii", &slkpin, &datapin);

        bcm2835_init();

        bcm2835_gpio_fsel(slkpin, BCM2835_GPIO_FSEL_OUTP);
        bcm2835_gpio_fsel(datapin, BCM2835_GPIO_FSEL_INPT);

        bcm2835_gpio_write(slkpin, HIGH);
        bcm2835_gpio_write(slkpin, LOW);

        int v = bcm2835_gpio_lev(datapin);

        bcm2835_close();

        return Py_BuildValue("i", v);
}

static PyMethodDef QuickPulse_methods[] =
{
        {"DoQuickPulse", py_DoQuickPulse, METH_VARARGS},
        {NULL, NULL}
};

void initQuickPulse()
{
        (void) Py_InitModule("QuickPulse", QuickPulse_methods);
}
