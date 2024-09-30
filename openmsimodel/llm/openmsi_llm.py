from openmsimodel.graph.open_graph import OpenGraph
import networkx as nx
import openai
from transformers import GPT2Tokenizer, GPT2Model
from pathlib import Path
import random
random.seed(42)

class OpenMSI_LLM:
    def __init__(self, api_key):
        openai.api_key = api_key
        # self.tokenizer = GPT2Tokenizer.from_pretrained('gpt4')
        # self.model = GPT2Model.from_pretrained('gpt4')
    
    def load_graphml(self, file_path):
        return nx.read_graphml(file_path)
    
    def graph_to_sentences(self, graph):
        sentences = []
        experiment_id = random.randint(0, 100000)
        sentences.append(f"Experiment {experiment_id} Objects (Nodes) and their properties: \n")
        for node in graph.nodes(data=True):
            node_id, node_data = node
            node_sentence = f"Object {node_data.get('short_name')} represents {node_data.get('type', 'an unknown entity')}."
            sentences.append(node_sentence)
            for key in list(node_data.keys())[5:]:
                node_sentence = f"This object has {key} value of {node_data.get(key, 'Unknown')}. "
                sentences.append(node_sentence)
        
        sentences.append('\n')
        sentences.append(f"Experiment {experiment_id} Object Relationships (Edges): \n")
        for edge in graph.edges(data=True):
            source, target, edge_data = edge
            edge_sentence = f"{graph.nodes[source].get('short_name', 'Unknown')} {edge_data.get('relationship', 'is related to')} {graph.nodes[target].get('short_name', 'Unknown')}."
            sentences.append(edge_sentence)
            
        return sentences
    
    def build_context(self, paragraphs):
        return "\n".join(paragraphs)
    
    def ask_question_with_context(self, context, question):
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=f"Context: {context}\nQuestion: {question}\nAnswer:",
        )
        return response.choices[0].text.strip()
    
    def write_context(self, context, destination):
        def chunk_string(string, chunk_size):
            """Yield successive chunks of the specified size from the string."""
            for i in range(0, len(string), chunk_size):
                yield string[i:i + chunk_size]
    
        # Create chunks
        chunks = list(chunk_string(context, 4096))

        # Save chunks to separate files
        for i, chunk in enumerate(chunks):
            with open(f"{destination}_chunk_{i+1}.txt", "w") as file:
                file.write(chunk)
            
        # with open(destination, "w") as file:
        #     # Write the string to the file
        #     file.write(context)



def main():
    api_key = ""
    
    openmsi_llm = OpenMSI_LLM(api_key)
    target_folder = Path().absolute() / "output3"

    # graph = openmsi_llm.load_graphml("/srv/hemi01-j01/openmsimodel/openmsimodel/graph/open_graph_build_nb/output/Laser_shock_run.graphml")
    # subgraphs = OpenGraph.get_isolated_subgraphs(graph)
    # # subgraphs = OpenGraph.get_subbranches(graph)

    # selected_subgraphs = sorted(subgraphs, key=lambda sg: sg.number_of_nodes())[-15:]
    # OpenGraph.save_subgraphs(selected_subgraphs, target_folder)

    # for i, s in enumerate(selected_subgraphs):
    #     print(i, len(s.nodes))
    # sizes = [(i, len(subgraph.nodes)) for i, subgraph in enumerate(subgraphs)]
    # selected_subgraphs = sorted(sizes, key=lambda x: x[1])

    # sentences = []
    # for subgraph in selected_subgraphs:
    #     print(len(subgraph))
    #     sentences.append(" ".join(openmsi_llm.graph_to_sentences(subgraph)))
    # context = openmsi_llm.build_context(sentences)
    # print(f'Context length: {len(context)}')
    # openmsi_llm.write_context(context, target_folder / "context")
    # question = "What does node 1 represent?"
    answer = openmsi_llm.ask_question_with_context('hi', 'how are you?')
    print(answer)
    # print(answer)

if __name__ == "__main__":
    main()