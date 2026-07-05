import pandas as pd
from typing import List
from . import ExtractedPage

def extract_csv(file_path: str) -> List[ExtractedPage]:
    pages: List[ExtractedPage] = []
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return [ExtractedPage(page_number=1, content=f"Failed to parse CSV: {str(e)}", content_type="text")]
        
    num_rows = len(df)
    
    if num_rows <= 1000:
        # Small CSV: convert to markdown tables, 100 rows per page
        for i in range(0, num_rows, 100):
            chunk_df = df.iloc[i:i+100]
            markdown_table = chunk_df.to_markdown(index=False)
            pages.append(ExtractedPage(
                page_number=(i//100) + 1,
                content=markdown_table,
                content_type="table",
                metadata={"total_rows": num_rows, "chunk_start": i, "chunk_end": min(i+100, num_rows)}
            ))
    else:
        # Large CSV: generate statistical summary + sample rows
        summary_lines = [f"Large CSV Summary (Total rows: {num_rows})", ""]
        
        # Column names and dtypes
        summary_lines.append("Columns:")
        for col in df.columns:
            summary_lines.append(f"- {col} ({df[col].dtype})")
            
        summary_lines.append("\nNumeric Columns Summary:")
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            stats = numeric_df.agg(['min', 'max', 'mean']).to_dict()
            for col, stat_dict in stats.items():
                summary_lines.append(f"- {col}: min={stat_dict.get('min')}, max={stat_dict.get('max')}, mean={stat_dict.get('mean')}")
                
        summary_lines.append("\nCategorical Columns Summary (Top 5):")
        cat_df = df.select_dtypes(exclude=['number'])
        for col in cat_df.columns:
            top_counts = df[col].value_counts().head(5).to_dict()
            counts_str = ", ".join([f"{k}: {v}" for k, v in top_counts.items()])
            summary_lines.append(f"- {col}: {counts_str}")
            
        summary_lines.append("\nSample Rows:")
        sample_markdown = df.head(10).to_markdown(index=False)
        summary_lines.append(sample_markdown)
        
        pages.append(ExtractedPage(
            page_number=1,
            content="\n".join(summary_lines),
            content_type="text",
            metadata={"total_rows": num_rows, "is_summary": True}
        ))
        
    return pages
