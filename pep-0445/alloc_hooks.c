/* global variable, don't use a variable allocated on the stack! */
struct {
    PyMemAllocators pymem;
    PyMemAllocators pymem_raw;
    PyMemAllocators pyobj;
    size_t allocated;
} hook;

/* read_size_t() and write_size_t() are not needed if malloc() and realloc()
   always return a pointer aligned to sizeof(size_t) bytes */
static size_t read_size_t(const void *p)
{
    const unsigned char *q = (const unsigned char *)p;
    size_t result = *q++;
    int i;

    for (i = SST; --i > 0; ++q)
        result = (result << 8) | *q;
    return result;
}

static void write_size_t(void *p, size_t n)
{
    unsigned char *q = (unsigned char *)p + SST - 1;
    int i;

    for (i = SST; --i >= 0; --q) {
        *q = (unsigned char)(n & 0xff);
        n >>= 8;
    }
}

static int hook_malloc(void *ctx, size_t size)
{
    PyMemAllocators *alloc;
    char *ptr;

    size += sizeof(size_t);
    ptr = alloc->malloc(size);
    if (ptr != NULL) {
        write_size_t(ptr, size);
        ptr += sizeof(size_t);
        allocated += size;
    }
    return ptr;
}

static int hook_realloc(void *ctx, void *void_ptr, size_t new_size)
{
    PyMemAllocators *alloc;
    char *ptr, *ptr2;
    size_t old_size;

    ptr = void_ptr;
    if (ptr) {
        ptr -= sizeof(size_t);
        old_size = read_size_t(ptr);
    }
    else {
        old_size = 0;
    }

    ptr2 = alloc->realloc(ptr, size);
    if (ptr2 != NULL) {
        write_size_t(ptr2, size);
        ptr2 += sizeof(size_t);
        allocated -= old_size;
        allocated += new_size;
    }
    return ptr2;
}

static void hook_free(void *ctx, void *void_ptr)
{
    PyMemAllocators *alloc;
    char *ptr;
    size_t size;

    ptr = void_ptr;
    if (!ptr)
        return;

    ptr -= sizeof(size_t);
    size = read_size_t(ptr);

    alloc->free(ptr);
    allocated -= size;
}

/* Must be called before the first allocation, or hook_realloc() and
   hook_free() will crash */
void setup_custom_allocators(void)
{
    PyMemAllocators alloc;

    alloc.malloc = my_malloc;
    alloc.realloc = my_realloc;
    alloc.free = my_free;

    /* disabled: the hook is not thread-safe */
#if 0
    PyMem_GetRawAllocators(&alloc.pymem_raw);
    alloc.ctx = &alloc.pymem_raw;
    PyMem_SetRawAllocators(&alloc);
#endif

    PyMem_GetAllocators(&alloc.pymem);
    alloc.ctx = &alloc.pymem;
    PyMem_SetAllocators(&alloc);

    PyObject_GetAllocators(&alloc.pyobj);
    alloc.ctx = &alloc.pyobj;
    PyObject_SetAllocators(&alloc);
}
