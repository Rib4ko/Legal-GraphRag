// Fallback mock dataset for demonstration when the backend or database (Qdrant / Neo4j) is offline.
export const DEMO_DATA = {
  default: {
    answer: "تُحدد المقتضيات القانونية شروط تأسيس الشركات التجارية بالمغرب وفقاً للقانون رقم 17-95 المتعلق بشركات المساهمة والقانون رقم 5-96 المتعلق بباقي الشركات التجارية. وتستوجب المسطرة إيداع النظام الأساسي، وتقييد الشركة بالسجل التجاري لدى كتابة الضبط بالمحكمة المختصة، مع الإشهار بالجريدة الرسمية وبجريدة الإعلانات القانونية.",
    expanded_query: "شروط وإجراءات تأسيس الشركات التجارية، السجل التجاري، والجريدة الرسمية بالمغرب",
    hits: [
      {
        id: "demo-chunk-101",
        score: 0.94,
        source: "ظهير شريف رقم 1.96.83 بتنفيذ القانون رقم 15.95 المتعلق بمدونة التجارة",
        article: "المادة 27 و28",
        content: "يجب على كل شخص ذاتي أو معنوي يكتسب صفة تاجر أن يقيد نفسه في السجل التجاري التابع للمحكمة الموجود بها مقر عمله الرئيسي، وذلك داخل أجل ثلاثة أشهر من تاريخ فتح المؤسسة التجارية."
      },
      {
        id: "demo-chunk-102",
        score: 0.89,
        source: "القانون رقم 5-96 المتعلق بالشركة ذات المسؤولية المحدودة",
        article: "المادة 51",
        content: "تودع العقود المتضمنة لعقد الشركة والنظام الأساسي بكتابة ضبط المحكمة الابتدائية التجارية الواقع بدائرتها مقر الشركة داخل أجل ثلاثين يوماً من تاريخ التأسيس."
      }
    ],
    graph_relationships: [
      {
        entity: "السجل التجاري",
        type: "OBLIGATION",
        target: "المحكمة التجارية المختصة",
        description: "إلزامية القيد والتقييد وفق مدونة التجارة لتمكين الشخصية المعنوية."
      },
      {
        entity: "النظام الأساسي للشركة",
        type: "DEPOSIT_AT",
        target: "كتابة الضبط",
        description: "إيداع رسمي خلال 30 يوماً من توقيع الشركاء."
      }
    ],
    translated_text: "Statutory legal provisions define the conditions for establishing commercial companies in Morocco pursuant to Law No. 17-95 on Joint Stock Companies and Law No. 5-96 on other commercial entities. The required procedure mandates filing the Articles of Association, registration in the Commercial Registry at the competent court registry, followed by official publication in the Official Gazette and recognized legal announcement bulletins."
  }
};
