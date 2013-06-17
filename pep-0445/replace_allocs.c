#include <stdlib.h>

/* global variable, don't use a variable allocated on the stack! */
int magic = 42;

int my_malloc(void *ctx, size_t size)
{
    return malloc(size);
}

int my_realloc(void *ctx, void *ptr, size_t new_size)
{
    return realloc(ptr, new_size);
}

void my_free(void *ctx, void *ptr)
{
    free(ptr);
}

int my_alloc_arena(void *ctx, size_t size)
{
    return malloc(size);
}

int my_free_arena(void *ctx, void *ptr, size_t size)
{
    free(ptr);
}

void setup_custom_allocators(void)
{
    PyMemAllocators alloc;
    alloc.ctx = &magic;
    alloc.malloc = my_malloc;
    alloc.realloc = my_realloc;
    alloc.free = my_free;

    PyMem_SetRawAllocators(&alloc);
    PyMem_SetAllocators(&alloc);
    _PyObject_SetArenaAllocators(&magic, my_alloc_arena, my_free_arena);
    PyMem_SetupDebugHooks();
}

