from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage
)


def create_index(filename: str):
    try:
        return _load_context(filename=filename)
    except:
        return _create_context(filename=filename)


def _load_context(filename: str):
    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/"+filename
    )
    index = load_index_from_storage(storage_context)
    return index


def _create_context(filename: str):
    directory = SimpleDirectoryReader(
        input_files=["docs/"+filename]
    ).load_data()
    index = VectorStoreIndex.from_documents(
        directory, show_progress=True)
    index.storage_context.persist(
        persist_dir="./storage/"+filename)
    return index
