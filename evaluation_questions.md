# أسئلة تقييم نظام (GraphRAG) للنصوص القانونية المغربية
# GraphRAG Evaluation Questions

تم استخراج هذه الأسئلة بناءً على نصوص قانونية حقيقية موجودة في قاعدة بيانات المشروع لاختبار قدرة نظام البحث الدلالي واستخراج العلاقات (GraphRAG) على الإجابة بدقة من السياق.

## 1. بناءً على: "القانون-الإطار رقم 69.19 المتعلق بالإصلاح الجبائي"
**(Tax Reform Framework Law 69.19)**

* **سؤال مباشر (Direct Question):** 
  ما هي الأهداف الأساسية للسياسة الجبائية للدولة كما حددها القانون-الإطار رقم 69.19؟
  *(What are the fundamental objectives of the state's tax policy as defined by Framework Law 69.19?)*

* **سؤال تحليلي / استنتاجي (Analytical Question):**
  كيف يهدف القانون-الإطار للإصلاح الجبائي إلى إدماج القطاع غير المهيكل في الاقتصاد المنظم؟ وما هي التدابير المحددة لذلك؟
  *(How does the tax reform framework law aim to integrate the informal sector into the formal economy? And what are the specific measures?)*

* **سؤال عن الاستثناءات والشروط (Conditions & Exceptions Question):**
  حسب المادة 8 من قانون الإصلاح الجبائي، ما هي الشروط والإجراءات الصارمة التي يجب الخضوع لها قبل منح أي تحفيز أو امتياز جبائي استثنائي؟
  *(According to Article 8 of the tax reform law, what are the strict conditions and procedures that must be met before granting any exceptional tax incentive?)*

* **سؤال عن الإجراءات المحددة (Specific Measures Question):**
  ما هي التدابير ذات الأولوية التي جاء بها القانون فيما يخص "الضريبة على القيمة المضافة" (TVA) والضريبة على الشركات؟
  *(What are the priority measures introduced by the law regarding Value Added Tax (VAT) and corporate tax?)*

---

## 2. بناءً على: "منشور وزير العدل رقم 2161 حول التصريح بالممتلكات للقضاة"
**(Minister of Justice Circular No. 2161 on Declaration of Assets for Judges)**

* **سؤال عن تحديد الفئات (Entity Identification Question):**
  من هم أفراد عائلة القاضي الذين يشملهم وجوب التصريح بالممتلكات العقارية والقيم المنقولة حسب منشور وزير العدل؟
  *(Which family members of a judge are included in the mandatory declaration of real estate and movable assets according to the Minister of Justice circular?)*

* **سؤال إجرائي (Procedural Question):**
  ما هو الإجراء الفوري المطلوب من القضاة الذين تغيرت وضعيتهم المادية أو الذين لم يقدموا تصريحهم منذ التحاقهم بالعمل؟
  *(What is the immediate action required from judges whose financial situation has changed or who have not submitted their declaration since joining the service?)*

* **سؤال عن البيانات التفصيلية (Detailed Data Extraction Question):**
  ما هي المعلومات الدقيقة التي يطلب نموذج "تصريح الأولاد القاصرين" تعبئتها بخصوص الممتلكات العقارية والقيم المنقولة؟
  *(What exact information does the "minor children's declaration" form require to be filled out regarding real estate and movable assets?)*

---

## 💡 كيفية اختبار هذه الأسئلة:
1. قم بنسخ السؤال باللغة العربية (أو الفرنسية إن قمت بترجمته).
2. ضعه في واجهة المستخدم (Search UI).
3. تحقق مما يلي:
   * **Semantic Search:** هل قام Qdrant بجلب النصوص الدقيقة المتعلقة بالقانون الصحيح؟
   * **Graph Context:** هل تمكن Neo4j من استخراج العلاقات بين الكيانات (مثلاً: القاضي -> يمتلك -> عقار، أو الإصلاح الجبائي -> ينظم -> القطاع غير المهيكل)؟
   * **LLM Synthesis:** هل صاغ نموذج (LLama/Groq) الإجابة بشكل صحيح بناءً على السياق فقط دون اختلاق معلومات؟
