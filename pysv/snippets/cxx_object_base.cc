class PySVObject {
public:
  PySVObject() = default;
  PySVObject(void* ptr): pysv_ptr(ptr) {}
  PySVObject(const PySVObject &obj) : pysv_ptr(obj.pysv_ptr) {}
  virtual ~PySVObject() = default;

  void *pysv_ptr = nullptr;
};