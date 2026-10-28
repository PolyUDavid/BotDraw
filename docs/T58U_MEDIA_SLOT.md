

## Kevin t58u 补丁（叠字 + 截图裁半 + AI 补槽）
- **边画边自检**：每区查叠字/骑边；OCR 过关仍须目视。
- **媒体完整**：禁止截图裁半；优先完整 ORIG 裁切。
- **AI 局部补图**：槽不和谐或不完整时，允许 GenerateImage 生成后插入图片槽；禁整页 AI；标签/公式仍矢量+OMML。
- 交付必有 `qa/<fig>_media_slots.json`；技能 [paper-figure-media-slot-harmony](sand-workflow:paper-figure-media-slot-harmony)。
