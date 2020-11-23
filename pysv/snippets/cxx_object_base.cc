class PySVObject {
public:
  void *pysv_ptr = nullptr;
  virtual ~PySVObject() = default;
};