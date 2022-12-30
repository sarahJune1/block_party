import matplotlib.pyplot as plt


def plot_counter(n, counter_dict, title):
    """
    Create bar chart from counter dictionary object
        Returns:
        Plot with meeting count topics.
    """
    topics = dict(counter_dict.most_common(n))
    labels, values = zip(*topics.items())
    fig, ax = plt.subplots(figsize = (10,5))
    plt.barh(labels,values,align='center') 
    # plt.title('Topics Counted for the week of: ' + start_date.strftime('%B %d, %Y'), fontsize=15)
    plt.xlabel('Meeting Count', fontsize=12)
    plt.ylabel('Topic', fontsize=12)
    plt.title(title, fontsize=15)
    #plt.xticks(range(min(values), max(values) + 1, 1))
    plt.tight_layout()

    