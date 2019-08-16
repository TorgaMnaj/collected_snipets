## Python 3.6 Script

## Created by Lakshmanan

## Modules needed
import multiprocessing
from multiprocessing import Pool

GLOBALLOCK = multiprocessing.Lock()

def generate_one_line_entry(plain_topic, paragraph, query_id, sim):
    GLOBALLOCK.acquire() ## Resource locking mechanism for Processes
    
    with open(get_filepath(castor_directory, castor_topics), 'a') as file:
        file.write('{}\n'.format(plain_topic))
        
    with open(get_filepath(castor_directory, castor_paragraphs), 'a') as file:
        file.write('{}\n'.format(paragraph))
    
    with open(get_filepath(castor_directory, castor_topic_ids), 'a') as file:
        file.write('{}\n'.format(query_id))
    
    with open(get_filepath(castor_directory, castor_samples), 'a') as file:
        file.write('{}\n'.format(sim))
        
    GLOBALLOCK.release() ## Release the lock as a line is written to all the necessary files

        
def generate_castor_files(topic):
  ### Data generation for file writing
  plain_topic = pre_process_topic(topic)
  para = get_para(docid)
  relevance = get_relevance(topic, docid)
  
  ## Call to worker
  generate_one_line_entry(plain_topic, para, topic, relevance)

            
def pool_handler():
    ## Desired number of Native Threads: multiprocessing.cpu_count()
    with Pool(multiprocessing.cpu_count()) as pool: ## Using "with" to close processes when done!!!
        pool.map(generate_castor_files, query_rel.keys())

if __name__ == "__main__":  # confirms that the code is under main function
    pool_handler()