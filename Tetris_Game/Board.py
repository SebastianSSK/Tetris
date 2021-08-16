from Tetris_Game.Settings import GRID_ROW_COUNT, GRID_COL_COUNT


class TetrisColumn:
    def __init__(self):
        self.column = [0 for _ in range(GRID_ROW_COUNT)]
        self.highest_index = -1
        self.number_of_wholes = 0

    def _count_number_of_wholes(self, prev_max_height, new_max_height):
        """count al holes with the given new height"""
        result = self.number_of_wholes
        sign = 1 if new_max_height > prev_max_height else -1
        for i in range(prev_max_height + sign, new_max_height, sign):
            result += sign if self.column[i] == 0 else 0
        return result

    def _update_number_of_wholes(self, prev_max_height, new_max_height):
        """find all new wholes that have formed between previous max height
        and new max height"""
        sign = 1 if new_max_height > prev_max_height else -1
        self.number_of_wholes += new_max_height - prev_max_height + sign

    def _find_next_highest_element(self, start_index=GRID_COL_COUNT - 1):
        """find next element starting at start index
        finds highest element at default"""
        for i in range(start_index, -1, -1):
            if self.column[i] != 0:
                return i
        # no next highest element exists
        return -1

    def _shift_elements_down(self, indices, has_highest_index):
        """:param indices list of all indices that were removed from the column
           :param has_highest_index boolean if indices contained that largest index of that column

           shifts all elements at positions bigger then any of the indices down depending on the
           number of indices the elements are higher as
        """
        shift = 1
        n = len(indices)
        # shift elements between indices
        for i in range(indices[n - 1] + 1, indices[0] + 1):
            if i < indices[n - shift - 1]:
                self.column[i - shift] = self.column[i]
                self.column[i] = 0
            elif i == indices[n - shift - 1]:
                shift += 1
        # indices do not contain the highest index
        if not has_highest_index:
            # all elements are shifted down that are higher then end index
            for i in range(indices[0] + 1, self.highest_index + 1):
                self.column[i - shift] = self.column[i]
            # highest columns are set to zero
            for i in range(self.highest_index + 1 - shift, self.highest_index + 1):
                self.column[i] = 0
            self.highest_index -= shift

    def increase_element(self, index):
        """increases counter by one"""
        # if counter zero add element at position
        if self.column[index] == 0:
            self.add_elements([1], [index])
        else:
            self.column[index] += 1

    def evaluate_position(self, indices):
        """
        :param indices positions that will be evaluated

        checks how a block at index would effect highest index and number of holes"""
        # get values without given index effecting them
        highest_index = self.highest_index
        number_of_holes = self.number_of_wholes
        # calculate effects
        if indices[0] > self.highest_index:
            highest_index = indices[0]
            number_of_holes = self._count_number_of_wholes(self.highest_index, highest_index) + 1
        return highest_index, number_of_holes - len(indices)

    def add_elements(self, elements, indices):
        """:param elements list containing the elements that will be added
           :param indices ordered list from highest to lowest
           of the positions where the elements will be added

           adds element at the indices to this column:"""
        # indices should not already contain an element
        if any([self.column[i] != 0 for i in indices]):
            raise IndexError("column already has element at given index ")
        n = len(indices)
        if indices[0] > self.highest_index:
            # check if new wholes were formed
            self._update_number_of_wholes(self.highest_index, indices[n - 1])
            self.highest_index = indices[0]
        else:
            self.number_of_wholes -= n
        # add elements to column
        for i, index in enumerate(indices):
            self.column[index] = elements[i]

    def remove_elements(self, indices):
        """removes entry at position index in column
        all elements at higher positions move down one position"""
        if any([self.column[i] == 0 for i in indices]):
            raise IndexError("column has no element at given index ")
        # remove elements at given indices
        for index in indices:
            self.column[index] = 0
        is_highest_element = indices[0] == self.highest_index
        # shift higher elements down
        self._shift_elements_down(indices, is_highest_element)
        # max height changed but no element has to move down
        if is_highest_element:
            self.highest_index = self._find_next_highest_element(indices[0] - 1)
            # check if new wholes were removed
            self._update_number_of_wholes(indices[0], self.highest_index)

    def has_element_at_position(self, y):
        return self.column[y] > 0

    def distance_to_next_element(self, y):
        """:param y position of the element
        :returns number of blocks between y and next highest block, if y is on a block returns -1"""
        return y - self.highest_index - 1 if y >= self.highest_index else y - self._find_next_highest_element(y) - 1


class TetrisBoard:
    def __init__(self):
        self.column_list = [TetrisColumn() for _ in range(GRID_COL_COUNT)]
        # count how many elements are in a given row
        self.row_counter_list = TetrisColumn()

    def _violates_constraints(self, shape, x, y):
        return x < 0 or x + len(shape) > GRID_COL_COUNT or y >= GRID_ROW_COUNT or y < 0

    def has_collision(self, shape, x, y):
        """
        :param shape more dimensional list containing a shape
        :param x position of shape
        :param y position of shape
        :returns if the shape at position x, y collides with any other block or the wall of the board"""
        if self._violates_constraints(shape, x, y):
            return True
        # for every line in shape
        for rel_x, line in enumerate(shape):
            for rel_y, val in enumerate(line):
                if val == 0:
                    continue
                # if column has already element at that position -> shape has collision
                if self.column_list[x + rel_x].has_element_at_position(y - rel_y):
                    return True
        return False

    def distance_to_collision(self, shape, x, y):
        """
        :param shape more dimensional list containing a shape
        :param x position of shape
        :param y position of shape
        :returns distance to collision regarding the given shape
        ans its coordinates x, y"""
        result = y + 1 - len(shape[0])
        if result < 0:
            return result

        # for every line of the shape
        for rel_x, line in enumerate(shape):
            for rel_y, val in enumerate(line):
                if val == 0:
                    continue
                distance = self.column_list[x + rel_x].distance_to_next_element(y - rel_y)
                # check if distance is smaller then current min distance
                if distance < result:
                    result = distance
                    # check if collision happened
                    if result < 0:
                        return result

        return result

    def place_shape(self, shape, x, y, distance_to_collision=None):
        """
        :param shape more dimensional list containing a shape
        :param x position of shape
        :param y position of shape
        :param distance_to_collision: optional distance to collision, if it is already known to prevent
        calculating values again
        :returns if shape was placed on the board
        """
        # check if distance is not known yet
        if distance_to_collision is None:
            distance_to_collision = self.distance_to_collision(shape, x, y)

        # set y value where the ship will be placed
        y -= distance_to_collision
        # if y coordinate is bigger or equal to GRID_ROW_COUNT -> shape can not be placed
        if y >= GRID_ROW_COUNT:
            return False
        # for every line in shape
        for rel_x, line in enumerate(shape):
            elements = []
            indices = []
            for rel_y, val in enumerate(line):
                if val == 0:
                    continue
                elements.append(val)
                indices.append(y - rel_y)
                # increase counter by one
                self.row_counter_list.increase_element(y - rel_y)
            self.column_list[x + rel_x].add_elements(elements, indices)
        return True

    def remove_full_rows(self):
        """:returns number of rows removed

        removed all rows that are full (not contain any zeros)"""
        # find all indices of of full rows
        remove_indices = [index for index in range(GRID_ROW_COUNT - 1, -1, -1)
                          if self.row_counter_list.column[index] == GRID_COL_COUNT]
        # check if any rows have to be removed
        if len(remove_indices) == 0:
            return 0
        # remove all of the found indices from all columns
        for column in self.column_list:
            column.remove_elements(remove_indices)
        # also remove the indices from counter list
        self.row_counter_list.remove_elements(remove_indices)
        # return number of rows removed
        return len(remove_indices)

    def evaluate_position(self, shape, x, y):
        distance_to_collision = self.distance_to_collision(shape, x, y)

        result = {"lines_cleared": 0,
                  "max_heights": [],
                  "number_of_holes": 0,
                  "bumpiness": [],
                  "valid": False}

        # set y value where the ship will be placed
        y -= distance_to_collision
        # if y coordinate is bigger or equal to GRID_ROW_COUNT -> shape can not be placed
        if self._violates_constraints(shape, x, y) or distance_to_collision < 0:
            # shape is not placeable at this position
            return result

        line_counter = [x for x in self.row_counter_list.column]
        hole_count_list = [column.number_of_wholes for column in self.column_list]
        heights = self.get_col_heights()
        # for every line in shape
        for rel_x, line in enumerate(shape):
            indices = []
            for rel_y, val in enumerate(line):
                if val == 0:
                    continue
                line_counter[y - rel_y] += 1
                indices.append(y - rel_y)
            height, number_of_holes = self.column_list[x + rel_x].evaluate_position(indices)
            hole_count_list[x + rel_x] = number_of_holes
            heights[x + rel_x] = height + 1

        result["lines_cleared"] = len([x for x in line_counter if x >= GRID_ROW_COUNT])
        # set number of holes
        result["number_of_holes"] = sum(hole_count_list)
        # set heights
        result["max_heights"] = sum(heights)
        # get bumpiness with test shape
        result["bumpiness"] = sum([abs(heights[i] - heights[i - 1]) for i in range(1, len(heights))])
        result["valid"] = True
        return result

    def reset_board(self):
        """clear board by deleting all columns"""
        self.column_list = [TetrisColumn() for _ in range(GRID_COL_COUNT)]
        # count how many elements are in a given row
        self.row_counter_list = TetrisColumn()

    def get_hole_count(self):
        """:returns number of wholes on the board"""
        result = 0
        for column in self.column_list:
            result += column.number_of_wholes
        return result

    def get_col_heights(self):
        """:returns list containing height of each column"""
        return [column.highest_index + 1 for column in self.column_list]

    def get_bumpiness(self):
        """:returns sum of differences between adjacent columns"""
        result = 0
        for i in range(1, GRID_COL_COUNT):
            result += abs(self.column_list[i].highest_index - self.column_list[i - 1].highest_index)
        return result

    def __str__(self):
        result = ""
        for i in range(GRID_ROW_COUNT):
            for j in range(GRID_COL_COUNT):
                result += str(self.column_list[j].column[GRID_ROW_COUNT - 1 - i]) + '-'
            result += "\n"

        return result
