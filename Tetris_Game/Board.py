from Tetris_Game.Settings import GRID_ROW_COUNT, GRID_COL_COUNT


class TetrisColumn:
    def __init__(self):
        self.column = [0 for _ in range(GRID_ROW_COUNT)]
        self.max_height = -1
        self.number_of_wholes = 0

    def _update_number_of_wholes(self, prev_max_height, new_max_height, sign):
        """find all new wholes that have formed between previous max height
        and new max height"""
        if sign != -1 and sign != 1:
            raise ValueError("sign should be either {} or {} not {}".format(-1, 1, sign))
        for i in range(prev_max_height + sign, new_max_height, sign):
            self.number_of_wholes += sign if self.column[i] == 0 else 0

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
            for i in range(indices[0] + 1, self.max_height + 1):
                self.column[i - shift] = self.column[i]
            # highest columns are set to zero
            for i in range(self.max_height + 1 - shift, self.max_height + 1):
                self.column[i] = 0
            self.max_height -= shift

    def increase_element(self, index):
        """increases counter by one"""
        # if counter zero add element at poition
        if self.column[index] == 0:
            self.add_elements([1], [index])
        else:
            self.column[index] += 1

    def add_elements(self, elements, indices):
        """:param elements list containing the elements that will be added
           :param indices ordered list from highest to lowest
           of the positions where the elements will be added

           adds element at the indices to this column:"""
        # indices should not already contain an element
        if any([self.column[i] != 0 for i in indices]):
            raise IndexError("column already has element at given index ")
        n = len(indices)
        if indices[0] > self.max_height:
            # check if new wholes were formed
            self._update_number_of_wholes(self.max_height, indices[n - 1], 1)
            self.max_height = indices[0]
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
        n = len(indices)
        # remove elements at given indices
        for index in indices:
            self.column[index] = 0
        is_highest_element = indices[0] == self.max_height
        # shift higher elements down
        self._shift_elements_down(indices, is_highest_element)
        # max height changed but no element has to move down
        if is_highest_element:
            self.max_height = self._find_next_highest_element(indices[0] - 1)
            # check if new wholes were removed
            self._update_number_of_wholes(indices[0], self.max_height, -1)

    def distance_to_next_element(self, y):
        """:param y position of the element
        :returns number of blocks between y and next block, does return -1 if a block exists at position y"""
        # print(y - self.max_height - 1, y - self._find_next_highest_element(y) - 1)
        return y - self.max_height - 1 if y >= self.max_height else y - self._find_next_highest_element(y) - 1


class TetrisBoard:
    def __init__(self):
        self.column_list = [TetrisColumn() for _ in range(GRID_COL_COUNT)]
        # count how many elements are in a given row
        self.row_counter_list = TetrisColumn()

    def has_collision(self, shape, x, y):
        """
        :param shape more dimensional list containing a shape
        :param x position of shape
        :param y position of shape
        :returns if the shape at position x, y collides with any other block or the wall of the board"""
        if x < 0 or x + len(shape) > GRID_COL_COUNT:
            return True
        try:
            result = self.distance_to_collision(shape, x, y)
            return result < 0
        # y coordinate is higher then board max
        except OverflowError:
            return True

    def distance_to_collision(self, shape, x, y):
        """
        :param shape more dimensional list containing a shape
        :param x position of shape
        :param y position of shape
        :returns distance to collision regarding the given shape
        ans its coordinates x, y"""
        result = y + 1 - len(shape[0])
        if y > GRID_ROW_COUNT:
            raise OverflowError("value {} is higher then max height {} of board".format(y, GRID_ROW_COUNT))
        elif result < 0:
            return result
        # for every line of the shape
        for rel_x, line in enumerate(shape):
            for rel_y, val in enumerate(line):
                if val == 0:
                    continue
                # check if column has already block at that index
                result = min(result, self.column_list[x + rel_x].distance_to_next_element(y - rel_y))
        return result

    def place_shape(self, shape, x, y, distance_to_collision=None):
        """
        :param shape more dimensional list containing a shape
        :param x position of shape
        :param y position of shape
        :param distance_to_collision: optional distance to collision, if it is already known to prevent
        calculating values again
        :returns if shape could be placed on the board
        """
        # set y value where the ship will be placed
        if distance_to_collision is None:
            y -= self.distance_to_collision(shape, x, y)
        else:
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

    def get_hole_count(self):
        """:returns number of wholes on the board"""
        result = 0
        for column in self.column_list:
            result += column.number_of_wholes
        return result

    def get_col_heights(self):
        """:returns list containing height of each column"""
        return [column.max_height for column in self.column_list]

    def get_bumpiness(self):
        """:returns sum of differences between adjacent columns"""
        result = 0
        for i in range(1, GRID_COL_COUNT):
            result += abs(self.column_list[i].max_height - self.column_list[i - 1].max_height)
        return result

    def __str__(self):
        result = ""
        for i in range(GRID_ROW_COUNT):
            for j in range(GRID_COL_COUNT):
                result += str(self.column_list[j].column[GRID_ROW_COUNT - 1 - i]) + '-'
            result += "\n"

        return result
