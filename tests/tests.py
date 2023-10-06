    # Tests that the function creates a 'pdfs' directory
# def test_create_directory(self):
from ..pipeline_website_api import start_batch
from ..imports import *
@pytest.mark.asyncio
async def test_create_directory(self):
    await start_batch()
    assert os.path.exists('pdfs')
    os.rmdir('pdfs')


# Tests that the function downloads PDF files from a URL
@pytest.mark.asyncio
async def test_download_pdf(self):
    await start_batch()
    assert os.path.exists('pdfs')
    assert len(os.listdir('pdfs')) > 0
    os.rmdir('pdfs')