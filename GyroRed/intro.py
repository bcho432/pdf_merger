
def read_text(song):
    with open(song, "r") as file:
        # Read lines one by one
        for line in file:
            print(line.strip())


def main():
    read_text("songs.txt")

if __name__ == "__main__":
    main()  # Call the main function to execute the program