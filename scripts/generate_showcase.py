"""Generate the homepage showcase and its reproducible standard samples."""
import sys
from render_standard_samples import main

if __name__ == "__main__":
    if "--showcase" not in sys.argv:
        sys.argv.append("--showcase")
    main()
